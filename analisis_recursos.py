#%%
import plotly.express as px
from carga_datos import *
from grafica_analisis import *
import streamlit as st
import google.generativeai as genai
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

from config import nota_pie
from contexto import *

def graf_evol_recursos(t):
  fig = px.line(presup_prov[['De Origen Provincial','De Origen Nacional']].rolling(t).mean(), title = "Recursos provinciales. Media móvil {}M a valores hoy".format(t))

  fig.update_layout(annotations=[dict(x=0, y=-0.2, xref='paper', yref='paper', text=nota_pie, showarrow=False)])
  return fig
# %%

peri_ini = '2016'
peri_act = presup_prov.index[-1].year
peri_fin = str(peri_act-1)
peri_act = str(peri_act)

rec_prom = presup_prov[['De Origen Provincial','De Origen Nacional']].loc[peri_ini:peri_fin].groupby(presup_prov.loc[peri_ini:peri_fin].index.month).mean()
presup_act  = presup_prov[['De Origen Provincial','De Origen Nacional']].loc[peri_act]
ult_mes = presup_act.index[-1].month

presup_act.loc[:,'prom_prov'] = rec_prom.iloc[:ult_mes,0].values
presup_act.loc[:,'prom_nac'] = rec_prom.iloc[:ult_mes,1].values
presup_act

# @title
def graf_comp_prom():
    fig = px.bar(presup_act[['De Origen Provincial', 'prom_prov']],barmode = 'group', title = 'Comparación recursos prov. con promedio')
    fig.update_layout(annotations=[dict(x=0, y=-0.2, xref='paper', yref='paper', text=nota_pie, showarrow=False)])
    fig.update_layout(
        annotations=[dict(x=0, y=-0.2, xref='paper', yref='paper', text=nota_pie, showarrow=False)],
        xaxis_title=None,  # Elimina el título del eje x
        yaxis_title=None   # Elimina el título del eje y
    )

    return fig


#%%
datos_relevantes = {
    "Periodos_de_quiebre" : "2016 con inicio de gobierno cambiemos. 2020 pandemia del COVID19. Noviembre 2023 victoria de Milei ",
    "Valor de los datos": "Los datos están expresados a valores hoy, por lo tanto tienen en cuenta el efecto inflacionario",
    "recursos": "Se ven los recursos de origen provincial que es lo que recauda la provincia por su propia cuenta. Por otro lado los recursos que coparticipa la nación",
    "Implicancias": "Los recursos son una buena proxy de la economía, si aumentan indica crecimiento de la economía.",
    "Tendencia" : "Luego de la tendencia alzista hasta 2016, los recursos muestran un estancamiento"
}


evol_recursos = graficar_y_analizar(explicacion_evol_recu, graf_evol_recursos,model)
evol_recursos.datos_relevantes(datos_relevantes)

# %%
comp_prom = graficar_y_analizar(explicacion_comp_prom,graf_comp_prom,model)

# %%
