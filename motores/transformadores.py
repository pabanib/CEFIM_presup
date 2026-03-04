"""
transformadores.py
===================
Custom transformers para el pipeline de clasificación de preguntas.

Estos transformers se importan antes de cargar los modelos guardados
para asegurar que están disponibles en la memoria.
"""

from sklearn.base import BaseEstimator, TransformerMixin
import re
import spacy
import subprocess
import sys

# Cargar modelo de lenguaje
nlp = None
try:
    nlp = spacy.load("es_core_news_lg")
except OSError:
    try:
        nlp = spacy.load("es_core_news_sm")
    except OSError:
        try:
            print("Descargando modelo de spacy (primera vez)...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "es_core_news_sm"], 
                                 stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            nlp = spacy.load("es_core_news_sm")
        except Exception as e:
            print(f"⚠️ Advertencia: No se pudo cargar modelo de spacy. Error: {e}")
            print("   El normalizador funcionará sin análisis lingüístico avanzado.")
            nlp = None

# Términos clave (igual que en entrenamiento.py)
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


def normalizar_pregunta(texto: str) -> str:
    """
    Aplica una serie de reglas de normalización y enmascaramiento para abstraer
    los parámetros de una pregunta y revelar su intención estructural.
    """
    texto_norm = texto.lower()

    # --- PASO 1: Normalización basada en Expresiones Regulares ---
    texto_norm = re.sub(r'\b\d+\s+(meses|años|días|trimestres|semestres|décadas)\b', '[PERIODO_RELATIVO]', texto_norm)
    texto_norm = re.sub(r'\b(de|del|desde|en|para el|al|año)\s+\d{4}\b', '[PERIODO_CONCRETO]', texto_norm)
    texto_norm = re.sub(r'\b\d{4}\b', '[PERIODO_CONCRETO]', texto_norm)

    # --- PASO 2: Normalización basada en Diccionarios ---
    for termino in sorted(TERMINOS_FINANCIEROS_CLAVE, key=len, reverse=True):
        if termino in texto_norm:
            texto_norm = texto_norm.replace(termino, '[RECURSO_FINANCIERO]')

    for termino, placeholder in TERMINOS_ESTADISTICOS.items():
        if termino in texto_norm:
            texto_norm = texto_norm.replace(termino, placeholder[0])

    # --- PASO 3: Normalización basada en spaCy (opcional) ---
    if nlp is not None:
        doc = nlp(texto_norm)
        tokens_procesados = []

        for token in doc:
            if token.lemma_ in ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]:
                tokens_procesados.append("[PERIODO_CONCRETO]")
            elif token.lemma_ in ["hoy", "ayer", "semana", "mes", "año", "trimestre", "semestre", "década", "quinquenio"]:
                if not (len(tokens_procesados) > 0 and tokens_procesados[-1] == "[PERIODO_RELATIVO]"):
                    tokens_procesados.append("[PERIODO_RELATIVO]")
            elif token.text.startswith("[") and token.text.endswith("]"):
                if not (len(tokens_procesados) > 0 and tokens_procesados[-1] == token.text):
                    tokens_procesados.append(token.text)
            elif not token.is_stop and not token.is_punct and not token.is_digit:
                tokens_procesados.append(token.lemma_)

        texto_final = " ".join(tokens_procesados)
        texto_final = re.sub(r'\s+', ' ', texto_final).strip()
    else:
        # Sin spacy: apenas limpiar espacios múltiples
        texto_final = re.sub(r'\s+', ' ', texto_norm).strip()

    return texto_final


class NormalizadorPreguntas(BaseEstimator, TransformerMixin):
    """
    Custom transformer que normaliza preguntas dentro del pipeline de sklearn.
    
    Encapsula la función normalizar_pregunta dentro de un transformer estándar
    de sklearn, permitiendo que se integre perfectamente en pipelines y que
    se guarde junto con el modelo.
    
    Ejemplo:
        >>> transformer = NormalizadorPreguntas()
        >>> questions = pd.Series(["¿Cuál es el promedio?", "¿Cómo evoluciona?"])
        >>> normalized = transformer.transform(questions)
    """
    
    def fit(self, X, y=None):
        """
        No requiere aprendizaje. Solo implementado por compatibilidad con sklearn.
        
        Args:
            X: Datos de entrada (no se usan)
            y: Target (no se usa)
            
        Returns:
            self: Retorna la instancia para permitir chaining
        """
        return self
    
    def transform(self, X):
        """
        Aplica normalización a cada pregunta en el conjunto de datos.
        
        Args:
            X: pd.Series o lista de preguntas (strings)
            
        Returns:
            pd.Series: Preguntas normalizadas
        """
        import pandas as pd
        # Convertir a Series si es una lista
        if not isinstance(X, pd.Series):
            X = pd.Series(X)
        return X.apply(normalizar_pregunta)
