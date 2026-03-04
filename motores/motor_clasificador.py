# motor_clasificador.py

import joblib
import sys
from pathlib import Path

# Asegurar que la clase NormalizadorPreguntas esté disponible cuando se cargue el modelo
from modelos.transformadores import NormalizadorPreguntas

class ClasificadorIntencion:
    def __init__(self, rutas_modelo=["modelo_periodo.joblib","modelo_estadistica.joblib"]): 
        """Carga el modelo de clasificación al inicializarse."""
        try:
            self.modelo_periodo = joblib.load(rutas_modelo[0])
            self.modelo_estadistica = joblib.load(rutas_modelo[1])
            print("✓ Modelos de clasificación cargados exitosamente.")
        except FileNotFoundError as e:
            print(f"❌ Error: No se encontró el archivo del modelo: {e}")
            self.modelo_periodo = None
            self.modelo_estadistica = None

    def predecir(self, texto_pregunta):
        """
        Predice la intención de una pregunta usando los modelos entrenados.
        
        Los modelos incluyen normalización integrada en el pipeline,
        por lo que la pregunta se procesa automáticamente.
        
        Args:
            texto_pregunta (str): La pregunta del usuario SIN normalizar
        
        Returns:
            dict: Diccionario con periodo y tipo de estadistica
        """
        if self.modelo_periodo is None or self.modelo_estadistica is None:
            return {"error": "Uno o más modelos de clasificación no están disponibles."}

        try:
            # ✓ No necesita normalizar aquí, el pipeline lo hace internamente
            periodo = self.modelo_periodo.predict([texto_pregunta])[0]
            estad = self.modelo_estadistica.predict([texto_pregunta])[0]
            
            return {
                'intencion': 'estadistica',
                'periodo': periodo,
                'estadistica': estad
            }
        except Exception as e:
            return {"error": f"Error en predicción: {str(e)}"}
