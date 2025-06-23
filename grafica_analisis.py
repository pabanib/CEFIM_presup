import joblib
from estadisticas import *

with open("cefim.txt", "r", encoding="utf-8") as f:
    cefim = f.read()


class graficar_y_analizar():
  def __init__(self, entorno, graficar, model, df):
    self.entorno = entorno
    self.grafico = graficar
    self.fig = None # Inicializa fig aquí
    self.df = df
    self.datos = {} # Inicializa datos aquí
    self.respuestas = {}
    self.model = model
    self.estadisticas = {}
  def __estadisticas(self, pregunta):
    mp = joblib.load("modelo_periodo.joblib")
    me = joblib.load("modelo_estadistica.joblib")
    peri, estad = mp.predict([pregunta])[0], me.predict([pregunta])[0]
    modelo_estadistico = AnalizadorEstadistico(self.df)
    self.estadisticas = modelo_estadistico.analizar(estad, peri)

  def graficar(self, *arg,**kwargs):
    fig = self.grafico(*arg,**kwargs)
    self.fig = fig
    return fig
  def datos_relevantes(self, datos = {}):
    self.datos = datos

  def analizar(self, pregunta):
    if self.datos == {}:
      datos_relevantes = 'No hay datos relevantes'
    else:
      for k,v in self.datos.items():
        datos_relevantes = f"{k}: {v}"
        break

    if self.respuestas == {}:
      resp_anteriores = 'No hay respuestas anteriores'
    else:
      for k, v in self.respuestas.items():
        resp_anteriores = f"{k}: {v}"
        break
    self.__estadisticas(pregunta)
    if self.estadisticas == {}:
      estadisticas = 'No hay estadísticas disponibles'
    else:
      for k, v in self.estadisticas.items():
        estadisticas = f"para la estadística {k}: el o los datos son {v}"

    texto = f"""Contesta la pregunta como si fueras un investigador del CEFIM {pregunta}, tenla en cuenta siempre como principal dato.
              Para contestar, ten en cuenta el gráfico {self.fig} como principal análisis, siempre toma en cuenta los últimos periodos para ser actualizada la respuesta.
              Si se pregunta por estadísticas o un anáilisis ten en cuenta los datos estadísticos que se encuentran en {estadisticas}.
              Además, si estás analizando la situación u opinando ten en cuenta los datos relevantes que estan en {datos_relevantes}, en caso de preguntas más directas no tomes en cuenta esto.
              También ten en cuenta el entorno de explicación del gráfico que es este para cuando haya que dar una explicación {self.entorno}.
              Ten en cuenta lo que opinan los especialistas en el CEFIM {cefim} sobre todo para dar opiniones sobre los análisis antes preguntas más directas no tengas en cuenta esto.
              Por último ten en cuenta las respuestas a las preguntas del usuario en {resp_anteriores}
              Contesta en un máximo de 200 palabras, no te extiendas demasiado y no repitas información innecesaria.
              """

    self.respuestas[pregunta] = self.model.generate_content(texto)
    return self.respuestas[pregunta]