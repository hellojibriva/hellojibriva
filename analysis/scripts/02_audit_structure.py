import pandas as pd, numpy as np
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 400); pd.set_option('display.max_columns', 50)
RAW = "/home/user/hellojibriva/analysis/data/WAHIS_Quantitative_data_20260910_RAW.csv"
df = pd.read_csv(RAW, encoding='utf-8-sig', dtype=str, keep_default_na=False)

NUM = ['New outbreaks','Susceptible','Cases','Killed and disposed of','Slaughtered','Deaths','Vaccinated']

print("=== HOW METRICS ARE POPULATED BY ANIMAL CATEGORY ===")
print("(count of rows where value is '-' i.e. structurally absent, vs numeric)\n")
for cat, g in df.groupby('Animal Category'):
    print(f"--- {cat}  (n={len(g)}) ---")
    rows=[]
    for c in NUM:
        dash = (g[c]=='-').sum()
        zero = (g[c]=='0').sum()
        pos  = len(g) - dash - zero
        rows.append({'metric':c,'dash(-)':dash,'zero':zero,'numeric>0':pos})
    print(pd.DataFrame(rows).to_string(index=False)); print()

print("=== SPECIES BY ANIMAL CATEGORY ===")
print(pd.crosstab(df['Animal Category'], df['Species']).T.to_string())

print("\n=== MEASURING UNITS BY ANIMAL CATEGORY ===")
print(pd.crosstab(df['Animal Category'], df['Measuring units']).to_string())

print("\n=== 'New outbreaks' non-dash rows, by category ===")
nb = df[df['New outbreaks']!='-']
print(nb['Animal Category'].value_counts())
print("\n=== 'Cases' non-dash rows, by category ===")
ca = df[df['Cases']!='-']
print(ca['Animal Category'].value_counts())

print("\n=== THE 4 'Wild' ROWS ===")
print(df[df['Animal Category']=='Wild'].to_string())

print("\n=== ROWS WITH Event_id or Outbreak_id populated ===")
print(df[(df['Event_id']!='-')|(df['Outbreak_id']!='-')].to_string())
