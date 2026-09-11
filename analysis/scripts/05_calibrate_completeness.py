import pandas as pd, numpy as np, itertools
RAW="/home/user/hellojibriva/analysis/data/WAHIS_Quantitative_data_20260910_RAW.csv"
df=pd.read_csv(RAW,encoding='utf-8-sig',dtype=str,keep_default_na=False)
df['Year']=df['Year'].astype(int)
DIS={'High pathogenicity avian influenza viruses (Inf. with) (poultry)':'HPAI','Rabies virus (Inf. with)':'Rabies','Trypanosomosis (tsetse-transmitted) (-2021)':'Trypanosomosis'}
df['dis']=df['Disease'].map(DIS)
TARGET={'HPAI':(203,192,11),'Rabies':(237,231,6),'Trypanosomosis':(57,56,1)}

def species_rows(d, yr0,yr1):
    return d[(d['Year']>=yr0)&(d['Year']<=yr1)&(d['Measuring units']=='Animal')]

for yr0,yr1 in [(2006,2023),(2006,2025),(2005,2026)]:
    s=species_rows(df,yr0,yr1)
    print(f"period {yr0}-{yr1}: species/animal-level rows by disease:", s.groupby('dis').size().to_dict(), "total", len(s))

print("\n--- calibrate 'complete' definition on 2006-2023 species rows ---")
s=species_rows(df,2006,2023)
cands=[['Cases','Killed and disposed of','Slaughtered','Deaths'],
       ['Susceptible','Cases','Killed and disposed of','Slaughtered','Deaths'],
       ['Susceptible','Cases','Killed and disposed of','Slaughtered','Deaths','Vaccinated'],
       ['Cases','Deaths']]
for cv in cands:
    ok=True; out=[]
    for d,(tn,tc,tm) in TARGET.items():
        g=s[s['dis']==d]
        miss=g[cv].eq('-')
        complete=(~miss.any(axis=1)).sum(); allmiss=(miss.all(axis=1)).sum()
        out.append(f"{d}: n={len(g)} complete={complete} allmiss={allmiss} (target {tn}/{tc}/{tm})")
        if (len(g),complete,allmiss)!=(tn,tc,tm): ok=False
    print(("PASS " if ok else "     ")+str(cv)); [print("      ",o) for o in out]
