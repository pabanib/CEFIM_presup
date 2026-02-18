#%%
import streamlit as st
# Asumimos que todos estos archivos existen y tienen las funciones que definimos
from datos_y_analisis.carga_datos import cargar_y_procesar_datos
from datos_y_analisis.analisis_recursos import (
    calcular_media_movil,
    graf_evol_recursos,
    comparar_mes_a_mes,
    graf_comp_prom
)
from motores.motor_clasificador import ClasificadorIntencion
from motores.motor_ia_llm import RedactorEconomico, configurar_modelo_llm
import datos_y_analisis.estadisticas as estadisticas
from prompts.contexto import explicacion_evol_recu, explicacion_comp_prom

from config_base.database import init_db, guardar_interaccion

init_db()  # Aseguramos que la base de datos esté inicializada
# --- DEFINICIÓN DE NUESTRA CLASE "RECETA" ---
class UnidadDeAnalisis:
    def __init__(self, nombre, funcion_calculo, funcion_grafico, texto_contexto, kwargs_calculo={}):
        self.nombre = nombre
        self.funcion_calculo = funcion_calculo
        self.funcion_grafico = funcion_grafico
        self.texto_contexto = texto_contexto
        self.kwargs_calculo = kwargs_calculo
#%%
# --- CONFIGURACIÓN E INICIALIZACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Plataforma de Presupuesto de Mendoza", page_icon="📊", layout="wide")

# --- CACHEO DE RECURSOS PARA MÁXIMA EFICIENCIA ---
@st.cache_resource
def get_clasificador():
    return ClasificadorIntencion()

@st.cache_resource
def get_redactor():
    modelo_llm = configurar_modelo_llm()
    return RedactorEconomico(modelo_llm)

@st.cache_data
def get_datos():
    df_prov, _ = cargar_y_procesar_datos()
    return df_prov

# --- Carga de todos los componentes al inicio ---
clasificador = get_clasificador()
redactor = get_redactor()
df_provinciales = get_datos()

# --- DEFINICIÓN DE NUESTROS ANÁLISIS CURADOS ---
analisis_evolucion = UnidadDeAnalisis(
    nombre="Análisis de Evolución de Recursos",
    funcion_calculo=calcular_media_movil,
    funcion_grafico=graf_evol_recursos,
    texto_contexto=explicacion_evol_recu,
    kwargs_calculo={'t': 12}
)
analisis_comparacion = UnidadDeAnalisis(
    nombre="Comparación con Promedio Histórico",
    funcion_calculo=comparar_mes_a_mes,
    funcion_grafico=graf_comp_prom,
    texto_contexto=explicacion_comp_prom
)
todos_los_analisis = [analisis_evolucion, analisis_comparacion]


# --- CUERPO DE LA APLICACIÓN ---
st.title('📊 Plataforma Interactiva del Presupuesto de Mendoza')
st.markdown("Una herramienta del CEFIM para democratizar el acceso a los datos públicos.")
st.markdown("---")


# --- BUCLE GENÉRICO PARA RENDERIZAR TODOS TUS ANÁLISIS ---
for i, analisis in enumerate(todos_los_analisis):
    with st.container(border=True):
        st.header(analisis.nombre)

        # Llama a las funciones específicas de esta "receta"
        df_calculado = analisis.funcion_calculo(df_provinciales, **analisis.kwargs_calculo)
        figura = analisis.funcion_grafico(df_calculado,**analisis.kwargs_calculo)
        st.plotly_chart(figura, use_container_width=True)

        st.subheader('Conversa sobre este gráfico')
        pregunta = st.text_input(f"Haz una pregunta sobre {analisis.nombre}", key=f"pregunta_{i}")

        if pregunta:
            with st.spinner('Analizando...'):
                clasificacion = clasificador.predecir(pregunta)
                if clasificacion.get('intencion') == 'estadistica':
                    dato_preciso = estadisticas.ejecutar_analisis_estadistico(df_provinciales, clasificacion)
                    respuesta_final = redactor.redactar_respuesta_estadistica(
                        pregunta=pregunta,
                        diccionario_datos=dato_preciso,
                        contexto=analisis.texto_contexto
                    )
                    st.markdown(respuesta_final, unsafe_allow_html=True)
                    try:
                        
                        guardar_interaccion(
                            pregunta=pregunta,
                            clasificacion=clasificacion,
                            dato_recuperado=dato_preciso,
                            respuesta_final=respuesta_final
                        )
                    except Exception as e:
                        st.warning(f"Error al guardar la interacción: {e}")

                else:
                    st.warning("Aún no estoy preparado para ese tipo de preguntas.")
    st.markdown("---")