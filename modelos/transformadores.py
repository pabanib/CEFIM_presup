"""
transformadores.py
===================
Custom transformers para el pipeline de clasificación de preguntas.

Versión sin dependencia de spaCy — usa solo regex y diccionarios.
"""

from sklearn.base import BaseEstimator, TransformerMixin
import re

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
    "promedio": "[ESTADISTICA_PROMEDIO]",
    "media móvil": "[ESTADISTICA_MEDIA_MOVIL]",
    "media": "[ESTADISTICA_PROMEDIO]",
    "total": "[ESTADISTICA_AGREGACION]",
    "acumulado": "[ESTADISTICA_AGREGACION]",
    "suma": "[ESTADISTICA_AGREGACION]",
    "mejor": "[ESTADISTICA_MAXIMO]", "mayor": "[ESTADISTICA_MAXIMO]",
    "máximo": "[ESTADISTICA_MAXIMO]", "pico": "[ESTADISTICA_MAXIMO]",
    "más alto": "[ESTADISTICA_MAXIMO]",
    "peor": "[ESTADISTICA_MINIMO]", "menor": "[ESTADISTICA_MINIMO]",
    "mínimo": "[ESTADISTICA_MINIMO]", "más bajo": "[ESTADISTICA_MINIMO]",
    "variación": "[OPERACION_VARIACION]", "comparada": "[OPERACION_VARIACION]",
    "comparativa": "[OPERACION_VARIACION]", "aumentó": "[OPERACION_VARIACION]",
    "bajó": "[OPERACION_VARIACION]", "subió": "[OPERACION_VARIACION]",
    "cayó": "[OPERACION_VARIACION]", "creció": "[OPERACION_VARIACION]",
    "cambió": "[OPERACION_VARIACION]",
    "proporción": "[OPERACION_PORCENTAJE]", "porcentaje": "[OPERACION_PORCENTAJE]",
    "parte de": "[OPERACION_PORCENTAJE]", "participación": "[OPERACION_PORCENTAJE]",
    "representa": "[OPERACION_PORCENTAJE]",
    "evolución": "[OPERACION_SERIE_TIEMPO]", "evolucionado": "[OPERACION_SERIE_TIEMPO]",
    "serie": "[OPERACION_SERIE_TIEMPO]",
    "tendencia": "[OPERACION_TENDENCIA]",
    "proyección": "[OPERACION_PROYECCION]", "proyectar": "[OPERACION_PROYECCION]",
    "correlación": "[OPERACION_CORRELACION]", "correlacionada": "[OPERACION_CORRELACION]",
    "elasticidad": "[OPERACION_ECONOMETRICA]",
    "análisis econométrico": "[OPERACION_ECONOMETRICA]",
    "modelizar": "[OPERACION_ECONOMETRICA]",
    "impacto": "[OPERACION_IMPACTO]", "impactó": "[OPERACION_IMPACTO]",
    "eficiencia": "[ANALISIS_EFICIENCIA]", "desempeño": "[ANALISIS_EFICIENCIA]"
}

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

PERIODOS_RELATIVOS = [
    "hoy", "ayer", "semana", "mes", "año", "trimestre",
    "semestre", "década", "quinquenio"
]


def normalizar_pregunta(texto: str) -> str:
    """
    Aplica normalización y enmascaramiento para abstraer los parámetros
    de una pregunta y revelar su intención estructural.
    Versión sin spaCy — solo regex y diccionarios.
    """
    texto_norm = texto.lower()

    # --- PASO 1: Periodos con regex ---
    texto_norm = re.sub(
        r'\b\d+\s+(meses|años|días|trimestres|semestres|décadas)\b',
        '[PERIODO_RELATIVO]', texto_norm
    )
    texto_norm = re.sub(
        r'\b(de|del|desde|en|para el|al|año)\s+\d{4}\b',
        '[PERIODO_CONCRETO]', texto_norm
    )
    texto_norm = re.sub(r'\b\d{4}\b', '[PERIODO_CONCRETO]', texto_norm)

    # --- PASO 2: Meses ---
    patron_meses = r'\b(' + '|'.join(MESES) + r')\b'
    texto_norm = re.sub(patron_meses, '[PERIODO_CONCRETO]', texto_norm)

    # --- PASO 3: Periodos relativos ---
    patron_periodos = r'\b(' + '|'.join(PERIODOS_RELATIVOS) + r')\b'
    texto_norm = re.sub(patron_periodos, '[PERIODO_RELATIVO]', texto_norm)

    # --- PASO 4: Términos financieros (de mayor a menor longitud) ---
    for termino in sorted(TERMINOS_FINANCIEROS_CLAVE, key=len, reverse=True):
        if termino in texto_norm:
            texto_norm = texto_norm.replace(termino, '[RECURSO_FINANCIERO]')

    # --- PASO 5: Términos estadísticos (de mayor a menor longitud) ---
    for termino, placeholder in sorted(TERMINOS_ESTADISTICOS.items(), key=lambda x: len(x[0]), reverse=True):
        if termino in texto_norm:
            texto_norm = texto_norm.replace(termino, placeholder)

    # --- PASO 6: Limpiar espacios y signos de puntuación irrelevantes ---
    texto_norm = re.sub(r'[¿?¡!]', '', texto_norm)
    texto_norm = re.sub(r'\s+', ' ', texto_norm).strip()

    return texto_norm


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
        return self

    def transform(self, X):
        import pandas as pd
        if not isinstance(X, pd.Series):
            X = pd.Series(X)
        return X.apply(normalizar_pregunta)