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

# --- Aquí podrías tener un selector para diferentes clases de análisis ---
# tipo_analisis = st.sidebar.selectbox("Seleccionar Análisis", ["Recursos por Origen", "Gasto por Finalidad", ...])
# if tipo_analisis == "Recursos por Origen":
#     analisis_actual = AnalisisRecursos()
# elif tipo_analisis == "Gasto por Finalidad":
#     analisis_actual = AnalisisGasto() # Otra de tus clases

# Por ahora, usamos una sola clase para simplificar
# ...existing code...

try:
    st.header('Análisis de Recursos por Origen')
    t = 12
    figura = evol_recursos.graficar(t)
    st.plotly_chart(figura, use_container_width=True)

    st.subheader('Conversa con los Datos')
    pregunta = st.text_input("Haz una pregunta sobre el gráfico", key="pregunta_chat_evol")

    if pregunta:
        with st.spinner('Generando explicación...'):
            explicacion = evol_recursos.analizar(pregunta)
            st.markdown(explicacion.text)

except Exception as e:
    st.error(f"Ha ocurrido un error al procesar el análisis: {e}")

#%%

try:
    st.header('Comparación con promedio')
    figura = comp_prom.graficar()
    st.plotly_chart(figura, use_container_width=True)

    st.subheader('Conversa con los Datos')
    pregunta = st.text_input("Haz una pregunta sobre el gráfico", key="pregunta_chat_comp")

    if pregunta:
        with st.spinner('Generando explicación...'):
            explicacion = comp_prom.analizar(pregunta)
            st.markdown(explicacion.text)

except Exception as e:
    st.error(f"Ha ocurrido un error al procesar el análisis: {e}")

# ...existing code...