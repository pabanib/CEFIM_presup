# motor_ia_llm.py

import streamlit as st
import google.generativeai as genai

# Usamos @st.cache_resource para asegurarnos de que el modelo se configura una sola vez.
# Esto ahorra tiempo y llamadas innecesarias.
@st.cache_resource
def configurar_modelo_llm():
    """Configura y devuelve el modelo de IA generativa de Google."""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        modelo = genai.GenerativeModel('gemini-1.5-flash')
        return modelo
    except Exception as e:
        # Si hay un error (ej. falta la API key), lo mostramos en la app.
        st.error(f"Error al configurar el modelo de IA: {e}")
        return None

class RedactorEconomico:
    """
    Una clase dedicada a interactuar con el LLM para generar texto.
    No hace cálculos, solo redacta.
    """
    def __init__(self, modelo_llm):
        self.modelo = modelo_llm


    def redactar_respuesta_estadistica(self, pregunta, diccionario_datos, contexto):
        """
        Toma un DICCIONARIO de datos ya calculados y los presenta en un lenguaje natural.
        """
        if self.modelo is None: return "Error: Modelo de IA no disponible."

        # Convertimos el diccionario de datos en un texto legible para el prompt
        # Esto es clave para darle un contexto rico a la IA
        datos_texto = "\n".join([f"- {key}: {value}" for key, value in diccionario_datos.items()])

        prompt = f"""
        Eres un analista económico senior del CEFIM. Tu tarea es responder la pregunta del usuario de manera experta, utilizando el conjunto de datos estadísticos que te proporciono.

        **Pregunta del Usuario:**
        "{pregunta}"

        **Contexto General del Análisis:**
        "{contexto}"

        **Contexto cefim**
        Ten en cuenta la opinion del CEFIM para las respuestas.

        **Set de Datos Estadísticos Clave para tu Análisis (Esta es tu fuente de verdad):**
        {datos_texto}

        **Instrucciones Clave:**
        - Sintetiza la información. No te limites a listar los datos, úsalos para construir un pequeño párrafo analítico que responda a la pregunta.
        - Selecciona los datos más relevantes del set que te di para apoyar tu argumento.
        - Sé conciso y profesional.
        - Escribe en formato Markdown para que se vea bien en Streamlit y amigable para el usuario.
        - No inventes cifras ni saques conclusiones que no se sustenten en los datos provistos. En todo caso puedes concluir de acuerdo a los informes CEFIM.
        - En caso de que no tengas información usa las notas del CEFIM para responder.
        """
        try:
            respuesta = self.modelo.generate_content(prompt)
            return respuesta.text
        except Exception as e:
            return f"Error al generar la respuesta de la IA: {e}"