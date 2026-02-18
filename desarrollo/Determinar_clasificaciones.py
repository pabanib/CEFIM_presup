#%%
import spacy
from sentence_transformers import SentenceTransformer
import umap
import hdbscan
import pandas as pd
import plotly.express as px
import re 
#%%
# ---------------------------------------------------------------------------
# 1. DEFINICIÓN DE DICCIONARIOS Y PATRONES
# ---------------------------------------------------------------------------

# Usaremos un modelo de spaCy más completo que el 'sm' para mejorar el POS tagging y lematización
# Si no lo tienes, ejecuta: python -m spacy download es_core_news_lg
try:
    nlp = spacy.load("es_core_news_lg")
except OSError:
    print("Modelo 'es_core_news_lg' no encontrado. Por favor, ejecuta: python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_sm")


# Placeholder para conceptos o recursos específicos de tu dominio
# Tú eres el experto aquí, esta lista debe ser nutrida con tu conocimiento
TERMINOS_FINANCIEROS_CLAVE = [
    "ingresos brutos", "iibb", "impuesto automotor", "automotor",
    "impuesto inmobiliario", "inmobiliario", "impuesto a los sellos", "sellos",
    "coparticipación federal", "coparticipación municipal", "coparticipación",
    "recursos propios", "recursos de origen provincial", "recursos de origen nacional",
    "recursos totales", "presupuesto", "meta de recaudación", "gasto",
    "salarios públicos", "déficit", "superávit fiscal", "presión tributaria",
    "reforma fiscal", "alícuotas", "base imponible", "tasa de morosidad",
    "brecha fiscal", "tax gap", "evasión", "elusión", "pbi",
    "tipo de cambio", "dólares", "inflación", "actividad económica"
]

# Placeholder para tipos de operaciones/estadísticas
TERMINOS_ESTADISTICOS = {
    "promedio": ["[ESTADISTICA_PROMEDIO]"],
    "media": ["[ESTADISTICA_PROMEDIO]"],
    "media móvil": ["[ESTADISTICA_MEDIA_MOVIL]"],
    "total": ["[ESTADISTICA_AGREGACION]"],
    "acumulado": ["[ESTADISTICA_AGREGACION]"],
    "suma": ["[ESTADISTICA_AGREGACION]"],
    "mejor": ["[ESTADISTICA_MAXIMO]"], "mayor": ["[ESTADISTICA_MAXIMO]"], "máximo": ["[ESTADISTICA_MAXIMO]"], "pico": ["[ESTADISTICA_MAXIMO]"], "más alto": ["[ESTADISTICA_MAXIMO]"],
    "peor": ["[ESTADISTICA_MINIMO]"], "menor": ["[ESTADISTICA_MINIMO]"], "mínimo": ["[ESTADISTICA_MINIMO]"], "más bajo": ["[ESTADISTICA_MINIMO]"],
    "variación": ["[OPERACION_VARIACION]"], "comparada": ["[OPERACION_VARIACION]"], "comparativa": ["[OPERACION_VARIACION]"],
    "aumentó": ["[OPERACION_VARIACION]"], "bajó": ["[OPERACION_VARIACION]"], "subió": ["[OPERACION_VARIACION]"], "cayó": ["[OPERACION_VARIACION]"], "creció": ["[OPERACION_VARIACION]"], "cambió": ["[OPERACION_VARIACION]"],
    "proporción": ["[OPERACION_PORCENTAJE]"], "porcentaje": ["[OPERACION_PORCENTAJE]"], "parte de": ["[OPERACION_PORCENTAJE]"], "participación": ["[OPERACION_PORCENTAJE]"], "representa": ["[OPERACION_PORCENTAJE]"],
    "evolución": ["[OPERACION_SERIE_TIEMPO]"], "evolucionado": ["[OPERACION_SERIE_TIEMPO]"], "serie": ["[OPERACION_SERIE_TIEMPO]"],
    "tendencia": ["[OPERACION_TENDENCIA]"],
    "proyección": ["[OPERACION_PROYECCION]"], "proyectar": ["[OPERACION_PROYECCION]"],
    "correlación": ["[OPERACION_CORRELACION]"], "correlacionada": ["[OPERACION_CORRELACION]"],
    "elasticidad": ["[OPERACION_ECONOMETRICA]"], "análisis econométrico": ["[OPERACION_ECONOMETRICA]"], "modelizar": ["[OPERACION_ECONOMETRICA]"],
    "impacto": ["[OPERACION_IMPACTO]"], "impactó": ["[OPERACION_IMPACTO]"],
    "eficiencia": ["[ANALISIS_EFICIENCIA]"], "desempeño": ["[ANALISIS_EFICIENCIA]"]
}

# ---------------------------------------------------------------------------
# 2. FUNCIÓN DE NORMALIZACIÓN PRINCIPAL
# ---------------------------------------------------------------------------

def normalizar_pregunta(texto: str) -> str:
    """
    Aplica una serie de reglas de normalización y enmascaramiento para abstraer
    los parámetros de una pregunta y revelar su intención estructural.
    """
    texto_norm = texto.lower()

    # --- PASO 1: Normalización basada en Expresiones Regulares (Reglas de alta precedencia) ---

    # Normalizar rangos numéricos como "24 meses", "5 años", "12 meses"
    texto_norm = re.sub(r'\b\d+\s+(meses|años|días|trimestres|semestres|décadas)\b', '[PERIODO_RELATIVO]', texto_norm)
    # Normalizar años específicos ("desde 2018", "en 2023", "año 2014")
    texto_norm = re.sub(r'\b(de|del|desde|en|para el|al|año)\s+\d{4}\b', '[PERIODO_CONCRETO]', texto_norm)
    # Normalizar años solos
    texto_norm = re.sub(r'\b\d{4}\b', '[PERIODO_CONCRETO]', texto_norm)

    # --- PASO 2: Normalización basada en Diccionarios (Términos clave) ---

    # Iterar sobre los términos financieros de forma ordenada (los más largos primero) para evitar reemplazos parciales
    for termino in sorted(TERMINOS_FINANCIEROS_CLAVE, key=len, reverse=True):
        if termino in texto_norm:
            texto_norm = texto_norm.replace(termino, '[RECURSO_FINANCIERO]')

    # Iterar sobre los términos estadísticos
    for termino, placeholder in TERMINOS_ESTADISTICOS.items():
        if termino in texto_norm:
            texto_norm = texto_norm.replace(termino, placeholder[0])

    # --- PASO 3: Normalización basada en spaCy (Lematización y Entidades) ---

    doc = nlp(texto_norm)
    tokens_procesados = []

    for token in doc:
        # Lematizar meses y reemplazarlos
        if token.lemma_ in ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]:
            tokens_procesados.append("[PERIODO_CONCRETO]")
        # Lematizar términos temporales relativos
        elif token.lemma_ in ["hoy", "ayer", "semana", "mes", "año", "trimestre", "semestre", "década", "quinquenio"]:
             if not (len(tokens_procesados) > 0 and tokens_procesados[-1] == "[PERIODO_RELATIVO]"): # Evitar duplicados
                tokens_procesados.append("[PERIODO_RELATIVO]")
        # Mantener placeholders ya definidos
        elif token.text.startswith("[") and token.text.endswith("]"):
            if not (len(tokens_procesados) > 0 and tokens_procesados[-1] == token.text): # Evitar duplicados
                tokens_procesados.append(token.text)
        # Ignorar stopwords, puntuación y números sueltos, a menos que sean parte de una entidad ya reconocida
        elif not token.is_stop and not token.is_punct and not token.is_digit:
            tokens_procesados.append(token.lemma_)

    # Reconstruir la frase normalizada y eliminar espacios duplicados
    texto_final = " ".join(tokens_procesados)
    texto_final = re.sub(r'\s+', ' ', texto_final).strip()

    return texto_final
#%%


# 1. Cargar modelo de NLP para español
nlp = spacy.load("es_core_news_sm")

def enmascarar_entidades(texto):
    doc = nlp(texto)
    nuevo_texto = texto
    # Aquí la lógica es simple, se puede refinar
    for ent in doc.ents:
        nuevo_texto = nuevo_texto.replace(ent.text, f"[{ent.label_}]")
    return nuevo_texto

#%%
sql = """SELECT codipreg, pregunta
FROM preguntas_clasificadas
UNION ALL 

SELECT codipreg, pregunta
FROM preguntas_no_clasif
"""
import sys
sys.path.append(r"D:\Archivos\Codigos\funciones")
import sql_funciones.busca_datos as bd

data = bd.data_sql(cliente = 'casa', sql = sql, main_db = 'finanzas')


# Supongamos que tienes tus preguntas en un DataFrame
df = data.dataframe #pd.read_csv("tus_preguntas.csv") # Columna 'pregunta'

#%%

# 2. Aplicar máscara (Crucial para tu hipótesis)
df['pregunta_mask'] = df['pregunta'].apply(normalizar_pregunta)

#%%
# 3. Vectorizar
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embeddings = model.encode(df['pregunta_mask'].tolist(), show_progress_bar=True)

#%%

# 4. Reducir dimensiones (UMAP)
umap_embeddings = umap.UMAP(n_neighbors=15, 
                            n_components=2, 
                            metric='cosine').fit_transform(embeddings)

df['x'] = umap_embeddings[:, 0]
df['y'] = umap_embeddings[:, 1]

#%%
# 5. Clusterizar (HDBSCAN)
clusterer = hdbscan.HDBSCAN(min_cluster_size=5, gen_min_span_tree=True)
df['cluster'] = clusterer.fit_predict(embeddings) # Ojo: a veces es mejor clusterizar sobre UMAP, a veces sobre embeddings crudos. Probemos ambos.

# 6. Visualizar
fig = px.scatter(df, x='x', y='y', color='cluster', hover_data=['pregunta', 'pregunta_mask'])
fig.show()
# %%

df[df.cluster == -1]

# %%
