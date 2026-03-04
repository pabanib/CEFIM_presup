"""
Script para descargar modelos de spacy necesarios
Ejecutar una sola vez: python setup_spacy.py
"""

import subprocess
import sys

def descargar_modelo_spacy():
    """Descarga el modelo de lenguaje español de spacy"""
    try:
        import spacy
        try:
            spacy.load("es_core_news_lg")
            print("✓ Modelo es_core_news_lg ya está instalado")
        except OSError:
            print("Descargando es_core_news_lg...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "es_core_news_lg"])
            print("✓ es_core_news_lg descargado exitosamente")
    except ImportError:
        print("❌ spacy no está instalado. Ejecuta: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    descargar_modelo_spacy()
