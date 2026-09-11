import pandas as pd, numpy as np
from scipy import stats
RAW="/home/user/hellojibriva/analysis/data/WAHIS_Quantitative_data_20260910_RAW.csv"
raw=pd.read_csv(RAW,encoding='utf-8-sig',dtype=str,keep_default_na=False)
raw['Year']=raw['Year'].astype(int)
DIS={'High pathogenicity avian influenza viruses (Inf. with) (poultry)':'HPAI','Rabies virus (Inf. with)':'Rabies','Trypanosomosis (tsetse-transmitted) (-2021)':'Trypanosomosis'}
raw['dis']=raw['Disease'].map(DIS)
for c in ['New outbreaks','Cases','Deaths','Killed and disposed of','Slaughtered']:
    raw[c+'_n']=pd.to_numeric(raw[c].replace('-',np.nan),errors='coerce')
TARGET={'HPAI':0.828742,'Rabies':0.861944,'Trypanosomosis':0.795304}
s=raw[(raw.Year>=2006)&(raw.Year<=2023)]
ob=s.groupby(['dis','Year'])['New outbreaks_n'].sum(min_count=1)
ca=s.groupby(['dis','Year'])['Cases_n'].sum(min_count=1)
de=s.groupby(['dis','Year'])['Deaths_n'].sum(min_count=1)
derived={
 'cases_per_outbreak':(ca/ob),'deaths_per_outbreak':(de/ob),'deaths_per_case':(de/ca),
 'outbreak_share_of_period':(ob/ob.groupby('dis').transform('sum')),
 'cum_outbreak_share':None,'rank_of_outbreaks':None}
print("target:",TARGET)
for name,ser in derived.items():
    for d in TARGET:
        if ser is None:
            base=ob.loc[d].dropna()
            v = base.cumsum()/base.sum() if name=='cum_outbreak_share' else pd.Series(stats.rankdata(base.values),index=base.index)
        else:
            v=ser.loc[d].dropna()
        if len(v)<4: continue
        rho,p=stats.spearmanr(v.index.values,v.values)
        flag=" <<< MATCH" if abs(rho-TARGET[d])<5e-4 else ""
        print(f"  {name:26s} {d:15s} n={len(v)} rho={rho:+.6f}{flag}")
print("\nCONCLUSION: no specification reproduces the published Spearman coefficients.")
