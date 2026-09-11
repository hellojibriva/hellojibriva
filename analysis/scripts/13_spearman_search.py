import pandas as pd, numpy as np, itertools
from scipy import stats
RAW="/home/user/hellojibriva/analysis/data/WAHIS_Quantitative_data_20260910_RAW.csv"
raw=pd.read_csv(RAW,encoding='utf-8-sig',dtype=str,keep_default_na=False)
raw['Year']=raw['Year'].astype(int)
DIS={'High pathogenicity avian influenza viruses (Inf. with) (poultry)':'HPAI','Rabies virus (Inf. with)':'Rabies','Trypanosomosis (tsetse-transmitted) (-2021)':'Trypanosomosis'}
raw['dis']=raw['Disease'].map(DIS)
for c in ['New outbreaks','Cases','Deaths','Killed and disposed of','Slaughtered','Susceptible','Vaccinated']:
    raw[c+'_n']=pd.to_numeric(raw[c].replace('-',np.nan),errors='coerce')
TARGET={'HPAI':(13,0.828742,0.000463),'Rabies':(18,0.861944,0.000004),'Trypanosomosis':(13,0.795304,0.001153)}
YVARS=['New outbreaks_n','Cases_n','Deaths_n','Killed and disposed of_n','Slaughtered_n','Susceptible_n','Vaccinated_n']

hits=[]
for y0,y1 in itertools.product(range(2005,2010),range(2020,2027)):
    s=raw[(raw.Year>=y0)&(raw.Year<=y1)]
    for yv in YVARS:
        piv=s.groupby(['dis','Year'])[yv].sum(min_count=1)
        for zf in (False,True):
            for d,(en,er,ep) in TARGET.items():
                try: v=piv.loc[d]
                except KeyError: continue
                if zf:
                    v=v.reindex(range(y0,y1+1)).fillna(0)
                else:
                    v=v.dropna()
                if len(v)<4: continue
                rho,p=stats.spearmanr(v.index.values,v.values)
                if abs(rho-er)<5e-4:
                    hits.append((d,y0,y1,yv,zf,len(v),rho,p,'n_MATCH' if len(v)==en else f'n={len(v)}!={en}'))
print("=== HITS on rho ===")
for h in hits: print("  ",h)
if not hits: print("   none")

print("\n=== Rabies decisive check: year vs reported outbreaks, several windows ===")
piv=raw.groupby(['dis','Year'])['New outbreaks_n'].sum(min_count=1)
for y0,y1 in [(2006,2023),(2006,2024),(2006,2025),(2005,2023),(2005,2025),(2008,2025),(2006,2026)]:
    v=piv.loc['Rabies'].reindex(range(y0,y1+1)).dropna()
    rho,p=stats.spearmanr(v.index.values,v.values)
    print(f"   Rabies {y0}-{y1}: n={len(v)} rho={rho:+.6f} p={p:.6g}")
print("\n=== HPAI same ===")
for y0,y1 in [(2006,2023),(2006,2024),(2006,2025),(2005,2025)]:
    v=piv.loc['HPAI'].reindex(range(y0,y1+1)).dropna()
    rho,p=stats.spearmanr(v.index.values,v.values)
    print(f"   HPAI {y0}-{y1}: n={len(v)} rho={rho:+.6f} p={p:.6g}")
print("\n=== Tryp same ===")
for y0,y1 in [(2006,2023),(2006,2025),(2008,2021)]:
    v=piv.loc['Trypanosomosis'].reindex(range(y0,y1+1)).dropna()
    rho,p=stats.spearmanr(v.index.values,v.values)
    print(f"   Tryp {y0}-{y1}: n={len(v)} rho={rho:+.6f} p={p:.6g}")

print("\n=== Reverse-engineer: what Sum d^2 / structure gives HPAI rho=0.828742 at n=13? ===")
n=13; rho=0.828742
print("   implied sum d^2 (no ties) =", (1-rho)*n*(n*n-1)/6)
print("   -> non-integer means it cannot be a plain untied Spearman on 13 ranks")
for d,(en,er,ep) in TARGET.items():
    n=en; print(f"   {d}: implied sum d^2 = {(1-er)*n*(n*n-1)/6:.3f}")
