# test_backend.py
#%%
# 1. Import all your "backend" specialists
from datos_y_analisis.carga_datos import cargar_y_procesar_datos
from motores.motor_clasificador import ClasificadorIntencion
import datos_y_analisis.estadisticas as estadisticas
#%%
def test_single_question(pregunta: str):
    """
    Tests the full backend pipeline for a single user question.
    """
    print("\n" + "="*50)
    print(f"🔬 Probando la pregunta: '{pregunta}'")
    print("="*50)

    # --- PASO 1: Cargar datos ---
    # In a real test suite, you might do this only once.
    try:
        df_prov, _ = cargar_y_procesar_datos()
        print("✅ [Paso 1] Datos cargados correctamente.")
    except Exception as e:
        print(f"❌ ERROR CRÍTICO en la carga de datos: {e}")
        return

    # --- PASO 2: Clasificar la pregunta ---
    try:
        clasificador = ClasificadorIntencion()
        if clasificador.modelo_periodo is None:
            raise ValueError("El modelo de clasificación no se cargó.")

        clasificacion = clasificador.predecir(pregunta)
        print("✅ [Paso 2] Clasificador ha respondido.")
        print(f"   👉 SALIDA DEL CLASIFICADOR: {clasificacion}") # <-- ¡AQUÍ VES LA SALIDA!
    except Exception as e:
        print(f"❌ ERROR en el clasificador: {e}")
        return

    # --- PASO 3: Calcular las estadísticas ---
    try:
        # Pasamos la salida del clasificador al motor de estadísticas
        resultado_estadistico = estadisticas.ejecutar_analisis_estadistico(df_prov, clasificacion)
        print("✅ [Paso 3] El motor de estadísticas ha respondido.")
        print(f"   👉 SALIDA DE ESTADÍSTICAS: {resultado_estadistico}") # <-- ¡AQUÍ VES EL RESULTADO FINAL!
    except Exception as e:
        print(f"❌ ERROR en el módulo de estadísticas: {e}")
        return
    
#%%
pregunta_que_se_rompio = "Podrías explicarme el gráfico?"
test_single_question(pregunta_que_se_rompio)

#%%
# --- El "Panel de Control" de tu Laboratorio ---
if __name__ == "__main__":
    # --- Prueba 1: La pregunta que funciona ---
    pregunta_que_funciona = "cuál es el promedio?"
    test_single_question(pregunta_que_funciona)

    # --- Prueba 2: La pregunta que se rompió ---
    # Cambia este texto por la pregunta exacta que te dio el error.
    pregunta_que_se_rompio = "Podrías explicarme el gráfico?"
    test_single_question(pregunta_que_se_rompio)

    # --- Prueba 3: Otra pregunta que quieras verificar ---
    # otra_pregunta = "mostrame el máximo"
    # test_single_question(otra_pregunta)