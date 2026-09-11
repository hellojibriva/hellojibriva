import pandas as pd, numpy as np
from scipy import stats
years=np.arange(2006,2024)
rab=np.array([1,2,23,24,5,11,19,31,9,2,1,51,91,71,107,147,178,150],float)
hp_y=np.array([2006,2007,2008,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023])
hp  =np.array([143,150,4,1,251,219,44,1,2,1,257,140,19],float)
tr_y=np.array([2008,2009,2010,2011,2012,2013,2014,2015,2017,2018,2019,2020,2021])
tr  =np.array([9,15,6,1,1,11,3,3,2,11,14,14,40],float)

def show(name,x,y,target):
    sp=stats.spearmanr(x,y); kt=stats.kendalltau(x,y); pe=stats.pearsonr(x,y)
    pl=stats.pearsonr(x,np.log1p(y))
    # manual spearman via ranks
    man=np.corrcoef(stats.rankdata(x),stats.rankdata(y))[0,1]
    print(f"{name:16s} n={len(x)}  target={target}")
    print(f"   spearman   rho={sp.statistic:+.6f} p={sp.pvalue:.6g}")
    print(f"   rank-pearson rho={man:+.6f}  (identity check with spearman)")
    print(f"   kendall    tau={kt.statistic:+.6f} p={kt.pvalue:.6g}")
    print(f"   pearson    r  ={pe.statistic:+.6f} p={pe.pvalue:.6g}")
    print(f"   pearson(log1p y) r={pl.statistic:+.6f} p={pl.pvalue:.6g}")
    # spearman on cumulative
    print(f"   spearman(cumsum y) rho={stats.spearmanr(x,np.cumsum(y)).statistic:+.6f}")
    # spearman on sorted y (mis-aligned series)
    print(f"   spearman(sorted y) rho={stats.spearmanr(x,np.sort(y)).statistic:+.6f}")
    print()

show("Rabies 06-23",years,rab,0.861944)
show("HPAI 06-23",hp_y,hp,0.828742)
show("Tryp 06-23",tr_y,tr,0.795304)

print("=== Could target rho come from a DIFFERENT n? Rabies rolling windows ===")
for a in range(0,6):
    for b in range(len(years),len(years)-6,-1):
        x,y=years[a:b],rab[a:b]
        if len(x)<8: continue
        r=stats.spearmanr(x,y).statistic
        if abs(r-0.861944)<5e-4: print("   HIT", years[a], years[b-1], len(x), r)
print("   (no hits printed = none found)")

print("\n=== p-value cross-check: what n/rho gives p=1.465797e-10 (Rabies target)? ===")
for n in range(10,25):
    for rho in np.arange(0.5,1.0,0.000001)[:0]: pass
# invert: for spearman, p from t-approx
from scipy.stats import t as tdist
for n in range(12,26):
    # solve rho such that two-sided p = 1.465797e-10
    target=1.465797e-10
    lo,hi=0.5,0.999999
    for _ in range(200):
        mid=(lo+hi)/2
        tt=mid*np.sqrt((n-2)/(1-mid**2)); p=2*tdist.sf(abs(tt),n-2)
        if p>target: lo=mid
        else: hi=mid
    print(f"   n={n}: rho implying p=1.4658e-10 is {lo:.6f}")
