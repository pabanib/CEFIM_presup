import pandas as pd

ep = pd.read_csv("https://raw.githubusercontent.com/pabanib/dataframes/master/presupuesto/presupuesto_mza.csv", sep=';')
partidas  = ep[['codipart','detapart']].groupby('codipart').first()

# @title
ep2 = ep.groupby(['peri','mes','detapart']).first()
presup_prov = ep2.importe_hoy.unstack()[[partidas.iloc[1].values[0],partidas.iloc[13].values[0],partidas.loc[20].values[0], partidas.loc[21].values[0], partidas.loc[25].values[0], partidas.loc[54].values[0],partidas.loc[43].values[0]]]
presup_valctes = ep2.importe.unstack()[[partidas.iloc[1].values[0],partidas.iloc[13].values[0],partidas.loc[20].values[0], partidas.loc[21].values[0], partidas.loc[25].values[0], partidas.loc[54].values[0],partidas.loc[43].values[0]]]
for c in presup_prov.columns:
  presup_prov[c] = presup_prov[c].apply(lambda x: float(str(x).replace(',','.')))
  presup_valctes[c] = presup_valctes[c].apply(lambda x: float(str(x).replace(',','.')))
presup_prov

ini = str(int(presup_prov.index[0][0]))+'-'+str(int(presup_prov.index[0][1]))
fin = str(int(presup_prov.index[-1][0]))+'-'+str(int(presup_prov.index[-1][1]))
peri = (pd.period_range(ini,fin,freq = 'M'))

presup_prov.index = peri.to_timestamp()