import streamlit as st
import sqlite3
import pandas as pd
import json

# --- CONFIGURACIÓN Y CONEXIÓN A LA BASE DE DATOS ---

DB_FILE = "log_publico.db"

# Estas son las categorías rígidas para la evaluación del clasificador.
# Siéntete libre de llenarlas con las opciones correctas.
POSIBLES_INTENCIONES = ["estadistica", "explicacion", "comparacion", "desconocido"]
POSIBLES_PERIODOS = ["Ultimo", "2023", "2024", "Acumulado"]
POSIBLES_ESTADISTICAS = ["variacion", "monto", "porcentaje_ingresos"]

def get_db_connection():
    """Establece conexión con la base de datos."""
    conn = sqlite3.connect(DB_FILE)
    # Usar Row Factory permite acceder a las columnas por nombre
    conn.row_factory = sqlite3.Row
    return conn

# --- FUNCIONES DE LÓGICA DE DATOS (Estilo directo) ---

def fetch_interaction_data(interaction_id):
    """
    Busca todos los datos asociados a un único ID de interacción:
    pregunta, datos de origen, respuestas de TODOS los modelos y sus evaluaciones existentes.
    """
    conn = get_db_connection()

    # 1. Obtener la interacción principal (pregunta, datos de origen, etc.)
    interaccion = conn.execute("SELECT * FROM interacciones WHERE id = ?", (interaction_id,)).fetchone()
    if not interaccion:
        return None, []

    # 2. Crear una lista de todas las respuestas a evaluar para esta interacción
    respuestas = []

    # Respuesta de nuestro modelo híbrido (id_modelo = 1)
    respuestas.append({
        "id_modelo": 1,
        "nombre_modelo": "Híbrido v1",
        "respuesta_generada": interaccion["respuesta_final"],
        "clasificacion_json": interaccion["clasificacion_json"]
    })

    # Respuestas de los modelos baseline
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
            "clasificacion_json": None # Los baselines no tienen esto
        })

    # 3. Obtener las evaluaciones YA existentes para esta interacción
    evals_nlg_rows = conn.execute("SELECT * FROM evaluaciones_nlg WHERE id_interaccion = ?", (interaction_id,)).fetchall()
    evals_clasificador_row = conn.execute("SELECT * FROM evaluaciones_clasificador WHERE id_interaccion = ?", (interaction_id,)).fetchone()

    # Anexar las evaluaciones existentes a cada respuesta correspondiente
    for resp in respuestas:
        # Buscar su evaluación NLG
        eval_nlg_existente = next((e for e in evals_nlg_rows if e["id_modelo"] == resp["id_modelo"]), None)
        resp["eval_nlg"] = dict(eval_nlg_existente) if eval_nlg_existente else None

        # Asignar la evaluación del clasificador solo al modelo híbrido
        if resp["id_modelo"] == 1:
            resp["eval_clasificador"] = dict(evals_clasificador_row) if evals_clasificador_row else None

    conn.close()
    return dict(interaccion), respuestas


def save_evaluation(eval_data):
    """
    Guarda o actualiza una evaluación en la base de datos.
    Usa INSERT OR REPLACE para simplificar el código (si existe, la reemplaza).
    """
    conn = get_db_connection()

    # Guardar la evaluación NLG
    conn.execute("""
        INSERT OR REPLACE INTO evaluaciones_nlg 
        (id_interaccion, id_modelo, faithfulness, relevance, fluency, coherence, style_alignment, comentarios)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        eval_data['id_interaccion'], eval_data['id_modelo'], eval_data['faithfulness'],
        eval_data['relevance'], eval_data['fluency'], eval_data['coherence'],
        eval_data['style_alignment'], eval_data['comentarios']
    ))

    # Guardar la evaluación del clasificador (si aplica)
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

# --- Panel Principal de Evaluación ---
if selected_id:
    # 1. Cargar todos los datos de la interacción seleccionada
    interaccion, respuestas = fetch_interaction_data(selected_id)

    if not interaccion:
        st.error(f"No se encontró ninguna interacción con el ID {selected_id}.")
    else:
        # 2. Mostrar la información común (pregunta y datos de origen)
        st.header(f"Evaluando Interacción #{selected_id}")
        st.subheader("Pregunta del Usuario:")
        st.markdown(f"> {interaccion['pregunta']}")

        with st.expander("Ver Datos de Origen (para evaluar Veracidad)", expanded=True):
            if interaccion['dato_recuperado']:
                try:
                    datos = json.loads(interaccion['dato_recuperado'])
                    st.json(datos)
                except:
                    st.text(interaccion['dato_recuperado'])
            else:
                st.info("No hay datos de origen estructurados para esta interacción.")

        st.divider()

        # 3. Iterar y mostrar un formulario de evaluación por CADA respuesta de modelo
        for respuesta in respuestas:
            # Separador visual para cada modelo
            st.subheader(f"Respuesta del Modelo: `{respuesta['nombre_modelo']}`")
            if respuesta['eval_nlg']:
                st.info("Esta respuesta ya ha sido evaluada. Puedes revisar o modificar la evaluación.")

            # Punto a cambiar 2: Renderizar la respuesta como Markdown
            st.markdown(respuesta['respuesta_generada'])

            # Usamos una key única para cada formulario
            with st.form(f"form_{respuesta['id_modelo']}", clear_on_submit=False):
                eval_nlg = respuesta['eval_nlg'] or {} # Diccionario vacío si no hay evaluación previa

                # --- Evaluación NLG ---
                st.write("**Evaluación de la Calidad de la Respuesta:**")
                cols = st.columns(3)
                faithfulness = cols[0].selectbox("Veracidad", [1,2,3,4,5], index=eval_nlg.get('faithfulness', 5)-1)
                relevance = cols[0].selectbox("Relevancia", [1,2,3,4,5], index=eval_nlg.get('relevance', 5)-1)
                fluency = cols[1].selectbox("Fluidez", [1,2,3,4,5], index=eval_nlg.get('fluency', 5)-1)
                coherence = cols[1].selectbox("Coherencia", [1,2,3,4,5], index=eval_nlg.get('coherence', 5)-1)
                style_alignment = cols[2].selectbox("Estilo CEFIM", [1,2,3,4,5], index=eval_nlg.get('style_alignment', 5)-1)

                comentarios = st.text_area("Comentarios", value=eval_nlg.get('comentarios', ''))

                # --- Evaluación del Clasificador (Solo para nuestro modelo) ---
                if respuesta['id_modelo'] == 1:
                    st.write("**Evaluación del Clasificador de Intención:**")
                    eval_clasif = respuesta['eval_clasificador'] or {}
                    predicciones = json.loads(respuesta['clasificacion_json'])

                    # Punto a cambiar 3: Usar selectbox para categorías rígidas
                    cols_clasif = st.columns(3)
                    intencion_pred_str = f"Predicción: {predicciones.get('intencion')}"
                    intencion_real = cols_clasif[0].selectbox("Intención Real", POSIBLES_INTENCIONES, 
                        index=POSIBLES_INTENCIONES.index(eval_clasif.get('intencion_real', POSIBLES_INTENCIONES[0])), help=intencion_pred_str)

                    periodo_pred_str = f"Predicción: {predicciones.get('periodo')}"
                    periodo_real = cols_clasif[1].selectbox("Periodo Real", POSIBLES_PERIODOS,
                        index=POSIBLES_PERIODOS.index(eval_clasif.get('periodo_real', POSIBLES_PERIODOS[0])), help=periodo_pred_str)

                    estadistica_pred_str = f"Predicción: {predicciones.get('estadistica')}"
                    estadistica_real = cols_clasif[2].selectbox("Estadística Real", POSIBLES_ESTADISTICAS,
                        index=POSIBLES_ESTADISTICAS.index(eval_clasif.get('estadistica_real', POSIBLES_ESTADISTICAS[0])), help=estadistica_pred_str)

                # --- Botón de envío ---
                if st.form_submit_button("💾 Guardar Evaluación para este Modelo"):
                    # Recopilar datos del formulario
                    form_data = {
                        "id_interaccion": selected_id,
                        "id_modelo": respuesta['id_modelo'],
                        "faithfulness": faithfulness,
                        "relevance": relevance,
                        "fluency": fluency,
                        "coherence": coherence,
                        "style_alignment": style_alignment,
                        "comentarios": comentarios
                    }
                    if respuesta['id_modelo'] == 1:
                        form_data.update({
                            "clasificacion_json": respuesta['clasificacion_json'],
                            "intencion_real": intencion_real,
                            "periodo_real": periodo_real,
                            "estadistica_real": estadistica_real
                        })

                    # Guardar y notificar
                    save_evaluation(form_data)
                    st.success(f"Evaluación para el modelo `{respuesta['nombre_modelo']}` guardada.")