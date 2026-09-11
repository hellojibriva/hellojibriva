import pandas as pd, numpy as np, sys
pd.set_option('display.width', 200); pd.set_option('display.max_rows', 300); pd.set_option('display.max_columns', 50)

RAW = "/home/user/hellojibriva/analysis/data/WAHIS_Quantitative_data_20260910_RAW.csv"
df = pd.read_csv(RAW, encoding='utf-8-sig', dtype=str, keep_default_na=False)

print("=== DIMENSIONS ==="); print(df.shape)
print("\n=== COLUMNS ==="); print(list(df.columns))
print("\n=== DTYPES (all read as str intentionally) ===")

print("\n=== YEAR ===")
print(df['Year'].value_counts().sort_index())
print("\n=== SEMESTER (raw values) ===")
print(df['Semester'].value_counts().sort_index())
print("\n=== WORLD REGION ==="); print(df['World region'].value_counts())
print("\n=== COUNTRY ==="); print(df['Country'].value_counts())
print("\n=== DISEASE ==="); print(df['Disease'].value_counts())
print("\n=== SEROTYPE ==="); print(df['Serotype/Subtype/Genotype'].value_counts())
print("\n=== ANIMAL CATEGORY ==="); print(df['Animal Category'].value_counts())
print("\n=== SPECIES ==="); print(df['Species'].value_counts())
print("\n=== MEASURING UNITS ==="); print(df['Measuring units'].value_counts())
print("\n=== EVENT_ID ==="); print(df['Event_id'].value_counts().head(20)); print("n unique Event_id:", df['Event_id'].nunique())
print("\n=== OUTBREAK_ID ==="); print(df['Outbreak_id'].value_counts().head(20)); print("n unique Outbreak_id:", df['Outbreak_id'].nunique())
print("\n=== ADMIN DIVISIONS: n unique ==="); print(df['Administrative Division'].nunique())
print(sorted(df['Administrative Division'].unique()))
