# -*- coding: utf-8 -*-
"""Publication figures, 2006-2025. Missing disease-years stay visibly missing:
lines BREAK across them (NaN) and each gap is explicitly annotated."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

OUT="/home/user/hellojibriva/analysis/outputs"; FIG="/home/user/hellojibriva/analysis/figures"
DISEASES=['HPAI','Rabies','Trypanosomosis']
COL={'HPAI':'#1b6ca8','Rabies':'#c0392b','Trypanosomosis':'#1e8449'}
MK ={'HPAI':'o','Rabies':'s','Trypanosomosis':'^'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,
 'axes.labelsize':11,'axes.spines.top':False,'axes.spines.right':False,
 'axes.grid':True,'grid.alpha':.25,'grid.linestyle':'-','grid.linewidth':.6,
 'figure.dpi':110,'savefig.dpi':300,'savefig.bbox':'tight','legend.frameon':False})

f1=pd.read_csv(f"{OUT}/Figure_1_Data.csv").set_index('Year')
f2=pd.read_csv(f"{OUT}/Figure_2_Data.csv").set_index('Year')
f3=pd.read_csv(f"{OUT}/Figure_3_Data.csv").set_index('Year')
f4=pd.read_csv(f"{OUT}/Figure_4_Data.csv")
YEARS=f1.index.values

def mark_missing(ax, series, y_frac=0.028, label_once=[True]):
    """Put an explicit 'no observation' tick under every missing disease-year."""
    miss=[y for y in YEARS if pd.isna(series[y])]
    if not miss: return miss
    y0,y1=ax.get_ylim(); yy=y0 - (y1-y0)*0 + (y1-y0)*y_frac if ax.get_yscale()=='linear' else y0*(1+y_frac)
    return miss

def gap_bands(ax, series, color):
    """Shade contiguous runs of missing disease-years so the break is unmistakable."""
    miss=sorted(y for y in YEARS if pd.isna(series[y]))
    runs=[]
    for y in miss:
        if runs and y==runs[-1][1]+1: runs[-1][1]=y
        else: runs.append([y,y])
    for a,b in runs:
        ax.axvspan(a-.5,b+.5,color=color,alpha=.07,zorder=0,lw=0)
    return runs

# ---------------------------------------------------------------- Figure 1
fig,axes=plt.subplots(3,1,figsize=(10,10),sharex=True)
for ax,d in zip(axes,DISEASES):
    s=f1[f"{d}_reported_outbreaks"]
    runs=gap_bands(ax,s,COL[d])
    ax.plot(YEARS,s.values,color=COL[d],lw=2,marker=MK[d],ms=6,mfc='white',mew=1.8,zorder=3)
    ax.set_ylabel("Reported outbreaks")
    nobs=int(s.notna().sum())
    ax.set_title(f"{d} — {nobs}/20 observed disease-years"+
                 (f"; no observations: {', '.join(str(int(y)) for y in YEARS if pd.isna(s[y]))}" if nobs<20 else ""),
                 loc='left',fontweight='bold')
    for a,b in runs:
        ax.text((a+b)/2,ax.get_ylim()[1]*.55,"no\nobservations",ha='center',va='center',
                fontsize=8,color='#666',style='italic')
axes[-1].set_xlabel("Year"); axes[-1].set_xticks(YEARS[::2])
fig.suptitle("Figure 1. Annual reported outbreaks by disease, Nigeria, WAHIS 2006–2025",
             fontsize=13,fontweight='bold',y=.995,x=.01,ha='left')
fig.text(.01,-.012,"Lines break across disease-years with no WAHIS observation; shaded bands mark those gaps. "
         "A gap denotes absence of reporting in the extracted dataset, not absence of disease.",
         fontsize=8.5,color='#555',ha='left')
fig.tight_layout(); fig.savefig(f"{FIG}/Figure_1_annual_reported_outbreaks.png"); plt.close(fig)

# ---------------------------------------------------------------- Figure 2
fig,ax=plt.subplots(figsize=(10,6))
allv=pd.concat([f2[f"{d}_reported_cases"] for d in DISEASES])
uselog = (allv.dropna()>0).all()
for d in DISEASES:
    s=f2[f"{d}_reported_cases"]
    ax.plot(YEARS,s.values,color=COL[d],lw=2,marker=MK[d],ms=6,mfc='white',mew=1.8,label=d,zorder=3)
if uselog: ax.set_yscale('log'); ax.set_ylabel("Reported cases (log scale)")
else: ax.set_ylabel("Reported cases")
ax.set_xlabel("Year"); ax.set_xticks(YEARS[::1]); ax.tick_params(axis='x',rotation=45)
h,l=ax.get_legend_handles_labels()
h.append(Line2D([],[],color='#999',lw=1.2,ls=(0,(2,2))));l.append("break = no WAHIS observation")
ax.legend(h,l,ncol=4,loc='upper left',bbox_to_anchor=(0,1.13))
ax.set_title("Figure 2. Annual reported cases by disease, Nigeria, WAHIS 2006–2025",
             loc='left',fontweight='bold',pad=34)
fig.text(.01,-.04,"Lines break across disease-years with no WAHIS observation. Logarithmic axis is used because "
         "reported case counts span several orders of magnitude across diseases.",fontsize=8.5,color='#555')
fig.tight_layout(); fig.savefig(f"{FIG}/Figure_2_annual_reported_cases.png"); plt.close(fig)
print("fig1, fig2 done; log scale used:",bool(uselog))

# ---------------------------------------------------------------- Figure 3
# Independent linear axes per disease so that HPAI's magnitude does not flatten
# Rabies and Trypanosomosis consequences.
CONS=[('deaths','Deaths','#b03a2e'),('killed_disposed','Killed and disposed of','#1f618d'),
      ('slaughtered','Slaughtered','#b9770e')]
fig,axes=plt.subplots(3,1,figsize=(10,10.5))
for ax,d in zip(axes,DISEASES):
    w=0.27
    for i,(key,lab,c) in enumerate(CONS):
        s=f3[f"{d}_{key}"]
        ax.bar(YEARS+(i-1)*w,s.values,width=w,color=c,label=lab,zorder=3)
    miss=[y for y in YEARS if pd.isna(f3[f"{d}_deaths"][y]) and pd.isna(f3[f"{d}_killed_disposed"][y])
          and pd.isna(f3[f"{d}_slaughtered"][y])]
    for y in miss: ax.axvspan(y-.5,y+.5,color='#888',alpha=.10,zorder=0,lw=0)
    top=np.nanmax([f3[f"{d}_{k}"].max() for k,_,_ in CONS])
    if np.isfinite(top) and top>0:
        for y in miss: ax.text(y,top*.5,"no obs.",ha='center',va='center',rotation=90,fontsize=7.5,color='#666',style='italic')
    ax.set_ylabel("Animals"); ax.set_xticks(YEARS[::2])
    ax.set_title(f"{d} (independent linear axis)",loc='left',fontweight='bold')
    ax.ticklabel_format(axis='y',style='plain')
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,_: f"{v:,.0f}"))
    if d=='HPAI': ax.legend(ncol=3,loc='upper left')
axes[-1].set_xlabel("Year")
fig.suptitle("Figure 3. Reported consequences by disease, Nigeria, WAHIS 2006–2025",
             fontsize=13,fontweight='bold',y=.998,x=.01,ha='left')
fig.text(.01,-.012,"Each panel uses an independent linear y-axis. Shaded years are disease-years with no WAHIS "
         "observation (not zero consequences). Absent bars within observed years are reported zeros.",
         fontsize=8.5,color='#555')
fig.tight_layout(); fig.savefig(f"{FIG}/Figure_3_reported_consequences.png"); plt.close(fig)

# ---------------------------------------------------------------- Figure 4
fig,axes=plt.subplots(1,3,figsize=(14,6))
for ax,d in zip(axes,DISEASES):
    t=f4[f4.Disease==d].sort_values('Reported_outbreaks')
    ax.barh(t['Administrative_Division'],t['Reported_outbreaks'],color=COL[d],zorder=3)
    for y,(v,p) in enumerate(zip(t['Reported_outbreaks'],t['Pct_of_national_reported_outbreaks'])):
        ax.text(v,y,f"  {int(v):,} ({p:.1f}%)",va='center',fontsize=8.5,color='#333')
    ax.set_xlim(0,t['Reported_outbreaks'].max()*1.42)
    ax.set_title(d,loc='left',fontweight='bold',color=COL[d])
    ax.set_xlabel("Reported outbreaks, 2006–2025"); ax.grid(axis='y',alpha=0)
fig.suptitle("Figure 4. Administrative divisions with the highest number of reported outbreaks, Nigeria, WAHIS 2006–2025",
             fontsize=13,fontweight='bold',y=1.02,x=.01,ha='left')
fig.text(.01,-.05,"Values are reported outbreaks and the percentage of that disease's national reported outbreaks. "
         "These describe the geographic concentration of REPORTED outbreaks, not true incidence, true prevalence or "
         "population-adjusted burden: the dataset contains no animal population denominators and no measure of "
         "reporting or diagnostic intensity.",fontsize=8.5,color='#555')
fig.tight_layout(); fig.savefig(f"{FIG}/Figure_4_top10_administrative_divisions.png"); plt.close(fig)
print("fig3, fig4 done")
