
# carga_datos.py

def cargar_y_procesar_datos():
    """
    Carga los datos del presupuesto desde la fuente original,
    los procesa y devuelve dos DataFrames: uno a valores corrientes
    y otro a valores constantes (hoy).
    """
    # Buena práctica: los imports que solo usa esta función, van adentro.
    import pandas as pd

    # 1. Carga de datos crudos desde la URL
    ep = pd.read_csv("https://raw.githubusercontent.com/pabanib/dataframes/master/presupuesto/presupuesto_mza.csv", sep=';')
    partidas = ep[['codipart', 'detapart']].groupby('codipart').first()

    # 2. Procesamiento y pivoteo de la tabla
    ep2 = ep.groupby(['peri', 'mes', 'detapart']).first()

    # Seleccionas las columnas que te interesan.
    # NOTA: Esta selección es un poco frágil. Si los códigos cambian, podría fallar.
    # Por ahora lo dejamos así, pero es un punto a tener en cuenta para el futuro.
    # Aquí se asume que las partidas tienen un orden específico y se seleccionan por su posición.
    columnas_recursos = [partidas.iloc[p].values[0] for p in range(20)]

    presup_prov = ep2.importe_hoy.unstack()[columnas_recursos]
    presup_valctes = ep2.importe.unstack()[columnas_recursos]

    # 3. Limpieza de formato de números
    for c in presup_prov.columns:
        presup_prov[c] = presup_prov[c].apply(lambda x: float(str(x).replace(',', '.')))
        presup_valctes[c] = presup_valctes[c].apply(lambda x: float(str(x).replace(',', '.')))

    # 4. Creación del índice de tiempo (esto está muy bien hecho)
    ini = str(int(presup_prov.index[0][0])) + '-' + str(int(presup_prov.index[0][1]))
    fin = str(int(presup_prov.index[-1][0])) + '-' + str(int(presup_prov.index[-1][1]))
    peri = pd.period_range(ini, fin, freq='M')

    presup_prov.index = peri.to_timestamp()
    presup_valctes.index = peri.to_timestamp()
    
    # 5. La función devuelve los dataframes listos para usar
    return presup_prov, presup_valctes
