#%%
import streamlit as st
import sys
from analisis_recursos import evol_recursos,comp_prom


# %%
# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Plataforma de Presupuesto de Mendoza",
    page_icon="📊",
    layout="wide"
)
# %%
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
                else:
                    st.warning("Aún no estoy preparado para ese tipo de preguntas.")
    st.markdown("---")