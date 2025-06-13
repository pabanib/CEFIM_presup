

class graficar_y_analizar():
  def __init__(self, entorno, graficar, model):
    self.entorno = entorno
    self.grafico = graficar
    self.fig = None # Inicializa fig aquí
    self.datos = {} # Inicializa datos aquí
    self.respuestas = {}
    self.model = model

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

    texto = f"""Contesta la pregunta {pregunta}, tenla en cuenta siempre como principal dato.
              Para contestar, ten en cuenta el gráfico {self.fig} como principal análisis, siempre toma en cuenta los últimos periodos para ser actualizada la respuesta.
              Además, ten en cuenta los datos relevantes que estan en {datos_relevantes}.
              También ten en cuenta el entorno de explicación del gráfico que es este {self.entorno}.
              Por último ten en cuenta las respuestas a las preguntas del usuario en {resp_anteriores}
              """

    self.respuestas[pregunta] = self.model.generate_content(texto)
    return self.respuestas[pregunta]