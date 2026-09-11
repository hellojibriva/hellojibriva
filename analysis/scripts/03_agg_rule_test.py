import pandas as pd, numpy as np
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
RAW = "/home/user/hellojibriva/analysis/data/WAHIS_Quantitative_data_20260910_RAW.csv"
df = pd.read_csv(RAW, encoding='utf-8-sig', dtype=str, keep_default_na=False)
df['Year']=df['Year'].astype(int)

DIS = {'High pathogenicity avian influenza viruses (Inf. with) (poultry)':'HPAI',
       'Rabies virus (Inf. with)':'Rabies',
       'Trypanosomosis (tsetse-transmitted) (-2021)':'Trypanosomosis'}
df['dis']=df['Disease'].map(DIS)
NUM = ['New outbreaks','Susceptible','Cases','Killed and disposed of','Slaughtered','Deaths','Vaccinated']
for c in NUM:
    df[c+'_n'] = pd.to_numeric(df[c].replace('-', np.nan), errors='coerce')

# row-type classification
def rowtype(r):
    if r['Animal Category']=='Both animal categories': return 'BOTH_outbreakrow'
    if r['Measuring units']=='-': return 'DOM_outbreakrow'
    if r['New outbreaks']!='-': return 'SPECIES_row_with_outbreaks(2026fmt)'
    return 'SPECIES_countrow'
df['rowtype']=df.apply(rowtype,axis=1)
print("=== ROW TYPES ==="); print(df['rowtype'].value_counts()); print()
print(pd.crosstab(df['Year'], df['rowtype']).to_string())

sub = df[(df['Year']>=2006)&(df['Year']<=2023)]
OLD = {'HPAI':dict(Outbreaks=1232,Cases=2650659,Deaths=1237397,Killed=4886232,Slaughtered=1748),
       'Rabies':dict(Outbreaks=923,Cases=2751,Deaths=618,Killed=624,Slaughtered=26),
       'Trypanosomosis':dict(Outbreaks=130,Cases=3008,Deaths=285,Killed=192,Slaughtered=77)}

print("\n\n=== RULE A: outbreaks = SUM(New outbreaks) over ALL rows; counts = SUM over all rows ===")
for d in ['HPAI','Rabies','Trypanosomosis']:
    g=sub[sub['dis']==d]
    new=dict(Outbreaks=g['New outbreaks_n'].sum(),Cases=g['Cases_n'].sum(),Deaths=g['Deaths_n'].sum(),
             Killed=g['Killed and disposed of_n'].sum(),Slaughtered=g['Slaughtered_n'].sum())
    for k,v in new.items():
        o=OLD[d][k]; print(f"{d:16s} {k:12s} old={o:>10,} new={int(v):>10,} diff={int(v)-o:>8,} {'PASS' if int(v)==o else 'FAIL'}")
    print()

print("=== RULE B: outbreaks = SUM(New outbreaks) on 'Both animal categories' rows ONLY ===")
for d in ['HPAI','Rabies','Trypanosomosis']:
    g=sub[(sub['dis']==d)&(sub['Animal Category']=='Both animal categories')]
    v=int(g['New outbreaks_n'].sum()); o=OLD[d]['Outbreaks']
    print(f"{d:16s} Outbreaks old={o:>6,} ruleB={v:>6,} diff={v-o:>6,} {'PASS' if v==o else 'FAIL'}")

print("\n=== RULE C: outbreaks = SUM(New outbreaks) on outbreak-rows only (BOTH + DOM_outbreakrow + 2026fmt) ===")
for d in ['HPAI','Rabies','Trypanosomosis']:
    g=sub[(sub['dis']==d)&(sub['rowtype']!='SPECIES_countrow')]
    v=int(g['New outbreaks_n'].sum()); o=OLD[d]['Outbreaks']
    print(f"{d:16s} Outbreaks old={o:>6,} ruleC={v:>6,} diff={v-o:>6,} {'PASS' if v==o else 'FAIL'}")

print("\n=== Do BOTH-rows and DOM_outbreakrows coexist in same Year/Semester/Disease/AdminDiv? ===")
key=['Year','Semester','dis','Administrative Division']
ob = df[df['rowtype'].isin(['BOTH_outbreakrow','DOM_outbreakrow'])]
ct = ob.groupby(key)['rowtype'].nunique()
print("keys with BOTH rowtypes present:", (ct>1).sum(), "of", len(ct))
if (ct>1).sum():
    bad = ct[ct>1].index[:5]
    for b in bad:
        print(df[(df['Year']==b[0])&(df['Semester']==b[1])&(df['dis']==b[2])&(df['Administrative Division']==b[3])].to_string())
