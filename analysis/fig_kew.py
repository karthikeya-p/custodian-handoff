"""Fig. 2: Kewaunee licensee-side submissions by author family and year."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rq4.py')).read().split('res = []')[0])
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif"], "font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
 "axes.edgecolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e"})
s=L[L.dockets.isin(['05000305'])&(L.date>='1997-01-01')].drop_duplicates(['AccessionNumber']).copy()
s['f']=s.n.map(fam); s['y']=s.date.dt.year
order=[("WPS","Wisconsin Public Service","#2a78d6"),("NMC","Nuclear Management Co.","#eb6834"),("Dominion","Dominion","#1baf7a"),("EnergySolutions group","Kewaunee Solutions","#eda100")]
t=s.groupby(['y','f']).size().unstack(fill_value=0).reindex(range(1997,2027),fill_value=0)
fig,ax=plt.subplots(figsize=(3.5,1.9)); bot=np.zeros(len(t))
for k,lab,col in order:
    v=t[k].values if k in t else np.zeros(len(t)); ax.bar(t.index,v,bottom=bot,color=col,width=0.8,label=lab,edgecolor="white",linewidth=0.4); bot+=v
oth=t.drop(columns=[k for k,_,_ in order if k in t]).sum(1).values
ax.bar(t.index,oth,bottom=bot,color="#c3c2b7",width=0.8,label="Other",edgecolor="white",linewidth=0.4)
for d in (2000+4.5/12, 2004+5.5/12, 2022+2.5/12): ax.axvline(d,color="#0b0b0b",lw=0.6,ls=":")
ax.set_ylabel("Licensee-side submissions"); ax.set_xlim(1996.4,2026.6)
ax.legend(frameon=False,fontsize=6.5,ncol=3,loc="lower center",bbox_to_anchor=(0.5,1.0),handlelength=1,columnspacing=0.8)
ax.grid(axis='y',color="#e6e5e1",lw=0.5); ax.set_axisbelow(True)
fig.tight_layout(pad=0.3)
for e in ("png","pdf"): fig.savefig(f"figs/fig_kewaunee.{e}",dpi=600)
