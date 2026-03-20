import streamlit as st
import sqlite3
import pandas as pd
import json

# --- CONFIGURACIÓN Y CONEXIÓN A LA BASE DE DATOS ---

DB_FILE = "log_publico.db"

POSIBLES_INTENCIONES = ["estadistica", "explicacion", "comparacion", "desconocido"]
POSIBLES_PERIODOS = ["ultimo", "historico", "periodo_especifico"]
POSIBLES_ESTADISTICAS = ["rec_actual", "variacion", "evolución", "estadistica_simple", "proporcion"]

# ID de modelo para el segundo modelo (ajustá este valor según tu tabla `modelos`)
ID_MODELO_OTRO = 2

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# --- FUNCIONES DE LÓGICA DE DATOS ---

def fetch_interaction_data(interaction_id, tabla="interacciones"):
    """
    Busca todos los datos asociados a un único ID de interacción.
    Soporta tanto 'interacciones' como 'interacciones_otra'.
    """
    conn = get_db_connection()

    interaccion = conn.execute(
        f"SELECT * FROM {tabla} WHERE id = ?", (interaction_id,)
    ).fetchone()

    if not interaccion:
        conn.close()
        return None, []

    respuestas = []

    if tabla == "interacciones":
        # Modelo híbrido principal (id_modelo = 1)
        respuestas.append({
            "id_modelo": 1,
            "nombre_modelo": "Híbrido v1",
            "respuesta_generada": interaccion["respuesta_final"],
            "clasificacion_json": interaccion["clasificacion_json"]
        })

        # Modelos baseline
        baseline_rows = conn.execute("""
            SELECT rb.id_modelo, rb.respuesta_generada, m.nombre_clave 
            FROM respuestas_baseline rb
            JOIN modelos m ON rb.id_modelo = m.id_modelo
            WHERE rb.id_interaccion = ?
        """, (interaction_id,)).fetchall()

        for row in baseline_rows:
            respuestas.append({
                "id_modelo": row["id_modelo"],
                "nombre_modelo": row["nombre_clave"],
                "respuesta_generada": row["respuesta_generada"],
                "clasificacion_json": None
            })

    else:  # interacciones_otra
        respuestas.append({
            "id_modelo": ID_MODELO_OTRO,
            "nombre_modelo": "Modelo Otro",
            "respuesta_generada": interaccion["respuesta_final"],
            "clasificacion_json": interaccion["clasificacion_json"]
        })

    # Evaluaciones NLG existentes para esta interacción
    evals_nlg_rows = conn.execute(
        "SELECT * FROM evaluaciones_nlg WHERE id_interaccion = ?", (interaction_id,)
    ).fetchall()

    evals_clasificador_row = conn.execute(
        "SELECT * FROM evaluaciones_clasificador WHERE id_interaccion = ?", (interaction_id,)
    ).fetchone()

    for resp in respuestas:
        eval_nlg_existente = next(
            (e for e in evals_nlg_rows if e["id_modelo"] == resp["id_modelo"]), None
        )
        resp["eval_nlg"] = dict(eval_nlg_existente) if eval_nlg_existente else None

        if resp["id_modelo"] == 1:
            resp["eval_clasificador"] = dict(evals_clasificador_row) if evals_clasificador_row else None

    conn.close()
    return dict(interaccion), respuestas


def save_evaluation(eval_data):
    conn = get_db_connection()

    conn.execute("""
        INSERT OR REPLACE INTO evaluaciones_nlg 
        (id_interaccion, id_modelo, faithfulness, relevance, fluency, coherence, style_alignment, comentarios)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        eval_data['id_interaccion'], eval_data['id_modelo'], eval_data['faithfulness'],
        eval_data['relevance'], eval_data['fluency'], eval_data['coherence'],
        eval_data['style_alignment'], eval_data['comentarios']
    ))

    if 'intencion_real' in eval_data:
        predicciones = json.loads(eval_data['clasificacion_json'])
        conn.execute("""
            INSERT OR REPLACE INTO evaluaciones_clasificador 
            (id_interaccion, intencion_pred, periodo_pred, estadistica_pred, intencion_real, periodo_real, estadistica_real)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            eval_data['id_interaccion'], predicciones.get('intencion'), predicciones.get('periodo'),
            predicciones.get('estadistica'), eval_data['intencion_real'],
            eval_data['periodo_real'], eval_data['estadistica_real']
        ))

    conn.commit()
    conn.close()


# --- COMPONENTE REUTILIZABLE: Panel de evaluación ---

def render_evaluation_panel(selected_id, tabla):
    """
    Renderiza el panel completo de evaluación para una tabla dada.
    Se usa tanto en el tab de Modelo Principal como en el de Modelo Otro.
    """
    interaccion, respuestas = fetch_interaction_data(selected_id, tabla=tabla)

    if not interaccion:
        st.error(f"No se encontró ninguna interacción con el ID {selected_id} en `{tabla}`.")
        return

    st.header(f"Evaluando Interacción #{selected_id}")
    st.subheader("Pregunta del Usuario:")
    st.markdown(f"> {interaccion['pregunta']}")

    with st.expander("Ver Datos de Origen (para evaluar Veracidad)", expanded=True):
        if interaccion.get('dato_recuperado'):
            try:
                datos = json.loads(interaccion['dato_recuperado'])
                st.json(datos)
            except Exception:
                st.text(interaccion['dato_recuperado'])
        else:
            st.info("No hay datos de origen estructurados para esta interacción.")

    st.divider()

    for respuesta in respuestas:
        # Clave única que incluye la tabla para evitar colisiones entre tabs
        form_key = f"form_{tabla}_{respuesta['id_modelo']}_{selected_id}"

        st.subheader(f"Respuesta del Modelo: `{respuesta['nombre_modelo']}`")

        if respuesta['eval_nlg']:
            st.info("Esta respuesta ya ha sido evaluada. Puedes revisar o modificar la evaluación.")

        st.markdown(respuesta['respuesta_generada'])

        with st.form(form_key, clear_on_submit=False):
            eval_nlg = respuesta['eval_nlg'] or {}

            st.write("**Evaluación de la Calidad de la Respuesta:**")
            cols = st.columns(3)
            faithfulness   = cols[0].selectbox("Veracidad",    [1,2,3,4,5], index=eval_nlg.get('faithfulness',   5)-1)
            relevance      = cols[0].selectbox("Relevancia",   [1,2,3,4,5], index=eval_nlg.get('relevance',      5)-1)
            fluency        = cols[1].selectbox("Fluidez",      [1,2,3,4,5], index=eval_nlg.get('fluency',        5)-1)
            coherence      = cols[1].selectbox("Coherencia",   [1,2,3,4,5], index=eval_nlg.get('coherence',      5)-1)
            style_alignment= cols[2].selectbox("Estilo CEFIM", [1,2,3,4,5], index=eval_nlg.get('style_alignment',5)-1)

            comentarios = st.text_area("Comentarios", value=eval_nlg.get('comentarios', ''))

            # Evaluación del clasificador solo para el modelo principal (id_modelo == 1)
            if respuesta['id_modelo'] == 1 and respuesta.get('clasificacion_json'):
                st.write("**Evaluación del Clasificador de Intención:**")
                eval_clasif = respuesta.get('eval_clasificador') or {}
                predicciones = json.loads(respuesta['clasificacion_json'])

                cols_clasif = st.columns(3)

                intencion_real = cols_clasif[0].selectbox(
                    "Intención Real", POSIBLES_INTENCIONES,
                    index=POSIBLES_INTENCIONES.index(eval_clasif.get('intencion_real', POSIBLES_INTENCIONES[0])),
                    help=f"Predicción: {predicciones.get('intencion')}"
                )
                periodo_real = cols_clasif[1].selectbox(
                    "Periodo Real", POSIBLES_PERIODOS,
                    index=POSIBLES_PERIODOS.index(eval_clasif.get('periodo_real', POSIBLES_PERIODOS[0])),
                    help=f"Predicción: {predicciones.get('periodo')}"
                )
                estadistica_real = cols_clasif[2].selectbox(
                    "Estadística Real", POSIBLES_ESTADISTICAS,
                    index=POSIBLES_ESTADISTICAS.index(eval_clasif.get('estadistica_real', POSIBLES_ESTADISTICAS[0])),
                    help=f"Predicción: {predicciones.get('estadistica')}"
                )

            if st.form_submit_button("💾 Guardar Evaluación para este Modelo"):
                form_data = {
                    "id_interaccion": selected_id,
                    "id_modelo":      respuesta['id_modelo'],
                    "faithfulness":   faithfulness,
                    "relevance":      relevance,
                    "fluency":        fluency,
                    "coherence":      coherence,
                    "style_alignment":style_alignment,
                    "comentarios":    comentarios
                }
                if respuesta['id_modelo'] == 1 and respuesta.get('clasificacion_json'):
                    form_data.update({
                        "clasificacion_json": respuesta['clasificacion_json'],
                        "intencion_real":     intencion_real,
                        "periodo_real":       periodo_real,
                        "estadistica_real":   estadistica_real
                    })

                save_evaluation(form_data)
                st.success(f"Evaluación para el modelo `{respuesta['nombre_modelo']}` guardada.")


# --- INTERFAZ DE STREAMLIT ---

st.set_page_config(layout="wide")
st.title("Herramienta de Evaluación Manual")

# --- Panel de Navegación ---
st.sidebar.header("Navegación")
selected_id = st.sidebar.number_input(
    "Selecciona el ID de la interacción a evaluar:",
    min_value=1,
    step=1
)

# --- Tabs principales ---
tab_principal, tab_otro = st.tabs(["📊 Modelo Principal", "🔬 Modelo Otro"])

if selected_id:
    with tab_principal:
        render_evaluation_panel(selected_id, tabla="interacciones")

    with tab_otro:
        render_evaluation_panel(selected_id, tabla="interacciones_otra")