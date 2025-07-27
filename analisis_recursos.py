#%%
#import google.generativeai as genai
#genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
#model = genai.GenerativeModel('gemini-2.0-flash')
import plotly.express as px
from config import nota_pie
from contexto import *

def calcular_media_movil(df, t, columnas = ['De Origen Provincial', 'De Origen Nacional']):
    """
    Calcula la media móvil de un DataFrame para una ventana de tiempo t.
    """
    return df[columnas].rolling(window=t).mean()

def graf_evol_recursos(df, t):
  fig = px.line(df, title = "Recursos provinciales. Media móvil {}M a valores hoy".format(t))

  fig.update_layout(annotations=[dict(x=0, y=-0.2, xref='paper', yref='paper', text=nota_pie, showarrow=False)])
  return fig
# %%

def comparar_mes_a_mes(df, columnas=['De Origen Provincial', 'De Origen Nacional']):
    # ...
    peri_act = df.index[-1].year # Reemplazamos presup_prov por df
    peri_fin = str(peri_act - 1)
    peri_ini = '2016'
    peri_act_str = str(peri_act)

    rec_prom = df[columnas].loc[peri_ini:peri_fin].groupby(df.loc[peri_ini:peri_fin].index.month).mean()
    presup_act = df[columnas].loc[peri_act_str] # Reemplazamos presup_prov por df
    ult_mes = presup_act.index[-1].month

    presup_act.loc[:, 'prom_prov'] = rec_prom.iloc[:ult_mes, 0].values
    presup_act.loc[:, 'prom_nac'] = rec_prom.iloc[:ult_mes, 1].values
    return presup_act


#%%
# @title
def graf_comp_prom(presup_act):
    """Genera un gráfico de barras comparando los recursos provinciales con el promedio mensual.
    """
    fig = px.bar(presup_act[['De Origen Provincial', 'prom_prov']],barmode = 'group', title = 'Comparación recursos prov. con promedio')
    fig.update_layout(annotations=[dict(x=0, y=-0.2, xref='paper', yref='paper', text=nota_pie, showarrow=False)])
    fig.update_layout(
        annotations=[dict(x=0, y=-0.2, xref='paper', yref='paper', text=nota_pie, showarrow=False)],
        xaxis_title=None,  # Elimina el título del eje x
        yaxis_title=None   # Elimina el título del eje y
    )

    return fig


#%%



