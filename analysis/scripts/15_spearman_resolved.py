import pandas as pd, numpy as np
from scipy import stats
RAW="/home/user/hellojibriva/analysis/data/WAHIS_Quantitative_data_20260910_RAW.csv"
raw=pd.read_csv(RAW,encoding='utf-8-sig',dtype=str,keep_default_na=False)
raw['Year']=raw['Year'].astype(int)
DIS={'High pathogenicity avian influenza viruses (Inf. with) (poultry)':'HPAI','Rabies virus (Inf. with)':'Rabies','Trypanosomosis (tsetse-transmitted) (-2021)':'Trypanosomosis'}
raw['dis']=raw['Disease'].map(DIS)
for c in ['New outbreaks','Cases']: raw[c+'_n']=pd.to_numeric(raw[c].replace('-',np.nan),errors='coerce')
s=raw[(raw.Year>=2006)&(raw.Year<=2023)]
ob=s.groupby(['dis','Year'])['New outbreaks_n'].sum(min_count=1)
ca=s.groupby(['dis','Year'])['Cases_n'].sum(min_count=1)
PUB={'HPAI':(13,0.828742,0.000463),'Rabies':(18,0.861944,0.000004),'Trypanosomosis':(13,0.795304,0.001153)}
print("HYPOTHESIS: published 'Spearman(year vs outbreaks)' is actually Spearman(outbreaks vs CASES),")
print("2006-2023, with unreported cases in an observed disease-year treated as 0.\n")
for d,(pn,pr,pp) in PUB.items():
    o=ob.loc[d].dropna()
    c=ca.loc[d].reindex(o.index).fillna(0)      # NA cases -> 0, the previously published convention
    rho,p=stats.spearmanr(o.values,c.values)
    ok = (len(o)==pn and abs(rho-pr)<5e-7 and abs(p-pp)<5e-7)
    print(f"{d:15s} n={len(o):2d} rho={rho:.6f} p={p:.6f}   published n={pn} rho={pr:.6f} p={pp:.6f}   {'*** EXACT MATCH ***' if ok else 'no'}")
print("\nFor contrast, the correctly specified test (calendar YEAR vs reported outbreaks, observed years only):")
for d,(pn,pr,pp) in PUB.items():
    o=ob.loc[d].dropna(); rho,p=stats.spearmanr(o.index.values,o.values)
    print(f"{d:15s} n={len(o):2d} rho={rho:+.6f} p={p:.6g}")
