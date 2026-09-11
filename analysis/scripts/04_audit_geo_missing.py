import pandas as pd, numpy as np
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
RAW = "/home/user/hellojibriva/analysis/data/WAHIS_Quantitative_data_20260910_RAW.csv"
df = pd.read_csv(RAW, encoding='utf-8-sig', dtype=str, keep_default_na=False)
df['Year']=df['Year'].astype(int)
DIS={'High pathogenicity avian influenza viruses (Inf. with) (poultry)':'HPAI','Rabies virus (Inf. with)':'Rabies','Trypanosomosis (tsetse-transmitted) (-2021)':'Trypanosomosis'}
df['dis']=df['Disease'].map(DIS)
df['nb']=pd.to_numeric(df['New outbreaks'].replace('-',np.nan),errors='coerce')

print("=== Nasarawa vs Nassarawa: years/diseases/outbreaks ===")
n=df[df['Administrative Division'].isin(['Nasarawa','Nassarawa'])]
print(n.groupby(['Administrative Division','Year','dis'])['nb'].agg(['size','sum']).to_string())

print("\n=== 'Nigeria' (national-level, unresolved state) rows ===")
g=df[df['Administrative Division']=='Nigeria']
print("n rows:", len(g))
print(g.groupby(['Year','dis'])['nb'].agg(['size','sum']).to_string())

print("\n=== LGA-style names by year (check confined to 2026) ===")
for a in ['Batagarawa','Gwale','Jos North','Toro','Ungogo']:
    print(a, sorted(df[df['Administrative Division']==a]['Year'].unique()))

print("\n=== Admin divisions present 2006-2025 ===")
s=df[(df['Year']>=2006)&(df['Year']<=2025)]
print(len(sorted(s['Administrative Division'].unique())), sorted(s['Administrative Division'].unique()))

print("\n=== DISEASE-YEAR PRESENCE MATRIX (row counts) 2005-2026 ===")
print(pd.crosstab(df['Year'], df['dis']).to_string())

print("\n=== Serotype text check: Trypanosomosis label & year span ===")
t=df[df['dis']=='Trypanosomosis']
print("label:", t['Disease'].unique(), "years:", sorted(t['Year'].unique()))

print("\n=== Plateau HPAI 2006-2023 outbreaks (validate vs 303) ===")
sub=df[(df['Year']>=2006)&(df['Year']<=2023)]
for d in ['HPAI','Rabies','Trypanosomosis']:
    gg=sub[sub['dis']==d].groupby('Administrative Division')['nb'].sum().sort_values(ascending=False).head(10)
    print(f"--- {d} ---"); print(gg.to_string())
