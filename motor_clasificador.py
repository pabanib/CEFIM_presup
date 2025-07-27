# motor_clasificador.py

import joblib

class ClasificadorIntencion:
    def __init__(self, rutas_modelo=["modelo_periodo.joblib","modelo_estadistica.joblib"]): 
        """Carga el modelo de clasificación al inicializarse."""
        try:
            self.modelo_periodo = joblib.load(rutas_modelo[0])
            self.modelo_estadistica = joblib.load(rutas_modelo[1])
            print("Modelo de clasificación cargado exitosamente.")
        except FileNotFoundError:
            self.modelo_periodo = None
            print(f"Error: No se encontró el archivo del modelo en {rutas_modelo[0]}")
            self.modelo_estadistica = None
            print(f"Error: No se encontró el archivo del modelo en {rutas_modelo[1]}")

    def predecir(self, texto_pregunta):
        """
        Predice la intención de una pregunta usando el modelo local.
        Devuelve un diccionario estructurado.
        """
        if self.modelo_periodo is None or self.modelo_estadistica is None:
            return {"error": "Uno o más modelos de clasificación no están disponibles."}

        # La lógica exacta aquí depende de cómo funcione tu modelo.
        # Asumimos que predice una o más etiquetas.
        periodo = self.modelo_periodo.predict([texto_pregunta])[0]
        estad = self.modelo_estadistica.predict([texto_pregunta])[0]

        # Aquí tendrías que mapear la predicción a tu formato estructurado.
        # Esto es un ejemplo, adáptalo a tu necesidad.
        # Por ahora, podemos simularlo:
        return {'intencion': 'estadistica','periodo': periodo, 'estadistica': estad}
