import pandas as pd, numpy as np, itertools
from scipy import stats
pd.set_option('display.width',260); pd.set_option('display.max_columns',40)
RAW="/home/user/hellojibriva/analysis/data/WAHIS_Quantitative_data_20260910_RAW.csv"
raw=pd.read_csv(RAW,encoding='utf-8-sig',dtype=str,keep_default_na=False)
raw['Year']=raw['Year'].astype(int)
DIS={'High pathogenicity avian influenza viruses (Inf. with) (poultry)':'HPAI','Rabies virus (Inf. with)':'Rabies','Trypanosomosis (tsetse-transmitted) (-2021)':'Trypanosomosis'}
raw['dis']=raw['Disease'].map(DIS)

print("### FAIL 8b: 2006 Rabies rows ###")
print(raw[(raw['Year']==2006)&(raw['dis']=='Rabies')].to_string())
print("\n### FAIL 8b: 2020 HPAI rows ###")
print(raw[(raw['Year']==2020)&(raw['dis']=='HPAI')].to_string())

print("\n### Are there OTHER observed disease-years with zero case-carrying records? ###")
num={}
for c in ['New outbreaks','Cases','Deaths','Killed and disposed of','Slaughtered']:
    num[c]=pd.to_numeric(raw[c].replace('-',np.nan),errors='coerce')
N=pd.DataFrame(num); N['Year']=raw['Year']; N['dis']=raw['dis']
s=N[(N.Year>=2006)&(N.Year<=2025)]
g=s.groupby(['dis','Year'])
rep=g.agg(rows=('Cases','size'), cases_nonnull=('Cases','count'), cases_sum=('Cases','sum'),
          ob_nonnull=('New outbreaks','count'))
print(rep[rep.cases_nonnull==0].to_string())

print("\n\n### FAIL 15b: Spearman candidate search (target HPAI .828742 n13, Rabies .861944 n18, Tryp .795304 n13) ###")
sub=N[(N.Year>=2006)&(N.Year<=2023)]
raws=raw[(raw['Year']>=2006)&(raw['Year']<=2023)]
cands={}
for m in ['New outbreaks','Cases','Deaths','Killed and disposed of','Slaughtered']:
    cands[m]=sub.groupby(['dis','Year'])[m].sum(min_count=1)
cands['n_raw_records']=raws.groupby(['dis','Year']).size().astype(float)
cands['n_admin_divisions']=raws.groupby(['dis','Year'])['Administrative Division'].nunique().astype(float)
cands['n_species']=raws.groupby(['dis','Year'])['Species'].apply(lambda s:s[s!=''].nunique()).astype(float)
cands['n_animal_records']=raws[raws['Measuring units']=='Animal'].groupby(['dis','Year']).size().astype(float)
TARGET={'HPAI':(13,0.828742),'Rabies':(18,0.861944),'Trypanosomosis':(13,0.795304)}
for name,ser in cands.items():
    line=[]
    for d,(en,er) in TARGET.items():
        try: v=ser.loc[d].dropna()
        except KeyError: line.append(f"{d}:NA"); continue
        if len(v)<3: line.append(f"{d}:n{len(v)}"); continue
        rho,p=stats.spearmanr(v.index.values,v.values)
        hit='<<<' if (len(v)==en and abs(rho-er)<1e-4) else ''
        line.append(f"{d}: n={len(v)} rho={rho:+.6f}{hit}")
    print(f"{name:22s} " + " | ".join(line))

print("\n### cumulative variants ###")
for name in ['New outbreaks','Cases']:
    ser=cands[name]; line=[]
    for d,(en,er) in TARGET.items():
        v=ser.loc[d].dropna().cumsum()
        rho,p=stats.spearmanr(v.index.values,v.values)
        line.append(f"{d}: n={len(v)} rho={rho:+.6f}")
    print(f"cumsum({name}):  "+" | ".join(line))
