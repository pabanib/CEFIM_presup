
import pandas as pd
from typing import Literal
"""
estadisticas = {}

df = presup_prov[['De Origen Provincial', 'De Origen Nacional']]

estadisticas['último periodo'] = df.iloc[-1]
estadisticas['promedio'] = df.mean()

cumsum = df.groupby(df.index.year).cumsum()
estadisticas['Recaudación acumulada últimos 5 años'] = cumsum[cumsum.index.month == df.iloc[-1].name.month].tail(5)
"""

# Clasificaciones válidas
T_Estadistica = Literal["rec_actual", "variacion", "promedio", "evolución", "max_min"]
T_Periodo = Literal["ultimo", "historico", "periodo_especifico"]

class AnalizadorEstadistico:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        #self.df["fecha"] = pd.to_datetime(self.df["fecha"])
    
    def analizar(self, tipo_estadistica: T_Estadistica, periodo: T_Periodo):
        #df_filtrado = self.filtrar_por_periodo(periodo, variable, periodo_especifico)
        df_filtrado = self.df.copy()

        if tipo_estadistica == "rec_actual":
            return self.recurso_actual(df_filtrado)
        elif tipo_estadistica == "variacion":
            return self.variacion(df_filtrado)
        elif tipo_estadistica == "promedio":
            return self.promedio(df_filtrado)
        elif tipo_estadistica == "evolución":
            return self.evolucion(df_filtrado)
        elif tipo_estadistica == "max_min":
            return self.maximo_minimo(df_filtrado)
        else:
            raise ValueError(f"Tipo de estadística no reconocida: {tipo_estadistica}")
    
    def filtrar_por_periodo(self, periodo: T_Periodo, variable: str, periodo_especifico: tuple = None) -> pd.DataFrame:
        df_var = self.df[self.df["variable"] == variable]
        if periodo == "ultimo":
            return df_var[df_var["fecha"].dt.year == self.df["fecha"].dt.year.max()]
        elif periodo == "historico":
            return df_var
        elif periodo == "periodo_especifico":
            if periodo_especifico is None:
                raise ValueError("Se requiere un período específico en formato (año_inicio, año_fin)")
            ini, fin = periodo_especifico
            return df_var[(df_var["fecha"].dt.year >= ini) & (df_var["fecha"].dt.year <= fin)]
        else:
            raise ValueError(f"Período no reconocido: {periodo}")

    # Funciones estadísticas (pueden ir mejorando con más lógica)
    def recurso_actual(self, df: pd.DataFrame):
        estadisticas = {}
        estadisticas['último periodo'] = df.iloc[-1]
        estadisticas['Acumulado en el año'] = df.resample('YE').sum().iloc[-1]
        estadisticas['últimos 5 años'] = df.resample('YE').mean().tail(5)
        estadisticas['promedio'] = df.mean()
        return estadisticas

    def variacion(self, df: pd.DataFrame):
        estadisticas = {}
        estadisticas['variacion_anual'] = df.resample('YE').mean().pct_change()
        estadisticas['variacion_mensual'] = df.resample('ME').mean().pct_change().tail(24)
        estadisticas['variacion_interanual'] = df.resample('ME').mean().pct_change(periods=12).tail(24)
        return estadisticas 
        
    def promedio(self, df: pd.DataFrame):
        estadisticas = {}
        estadisticas['promedio_anual'] = df.resample('YE').mean()
        estadisticas['promedio'] = df.mean()
        estadisticas['promedio_mes'] = df.groupby(df.index.month).mean()
        return estadisticas
 
    def evolucion(self, df: pd.DataFrame):
        estadisticas = {}
        estadisticas['tendencia_mensual'] = df.rolling(window=12).mean()
        estadisticas['tendencia_anual'] = df.resample('YE').mean().rolling(window=4).mean()
        return estadisticas

    def maximo_minimo(self, df: pd.DataFrame):
        estadisticas = {}
        estadisticas['maximo_historico_mensual'] = df.max()
        estadisticas['minimo_historico_mensual'] = df.min()
        estadisticas['maximo_historico_anual'] = df.resample('YE').mean().max()
        estadisticas['minimo_historico_anual'] = df.resample('YE').mean().min()
        
        return estadisticas


# --- NUEVA FUNCIÓN: La "Puerta de Entrada" o "Llave de Arranque" ---
def ejecutar_analisis_estadistico(df, clasificacion):
    """
    Recibe el DataFrame y la clasificación, usa la clase AnalizadorEstadistico
    y devuelve un DICCIONARIO de estadísticas relevantes.
    """
    tipo_estadistica = clasificacion.get('estadistica', 'rec_actual') # ej: 'promedio'
    periodo = clasificacion.get('periodo', 'historico') # ej: 'historico'

    # 1. Instanciamos tu potente clase
    analizador = AnalizadorEstadistico(df)
    
    # 2. Usamos tu método .analizar() para obtener el diccionario de estadísticas
    try:
        diccionario_de_stats = analizador.analizar(tipo_estadistica, periodo)
        return diccionario_de_stats
    except ValueError as e:
        return {"error": str(e)}