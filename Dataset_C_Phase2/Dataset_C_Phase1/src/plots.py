from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
from definitions import *

def make_plots(result,out):
    d=result['principal'];out=Path(out)
    font_manager.fontManager.addfont(str(out/'assets/fonts/B-NAZANIN.TTF'))
    plt.rcParams.update({'font.family':['B Nazanin','DejaVu Sans'],'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':False,'svg.fonttype':'path'})
    def finish(fig,name):
        fig.tight_layout()
        target=out/'figures'/f'{name}.png'
        tmp=target.with_name(name+'.tmp.png')
        fig.savefig(tmp,dpi=320,bbox_inches='tight')
        from PIL import Image
        with Image.open(tmp) as image: image.verify()
        tmp.replace(target)
        fig.savefig(out/'figures'/f'{name}.svg',bbox_inches='tight');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.4,3.5));n=[int(d.GROUP.eq(g).sum()) for g in GROUPS];x=np.arange(4)
    ax.bar(x,n,color=COLORS,width=.62);ax.set_xticks(x,list(GROUPS.values()),fontsize=9);ax.set_ylabel('Participants (count)');ax.set_ylim(0,max(n)*1.18);ax.set_title(f'Cognitive status | principal joint sample, N = {len(d)}')
    for i,v in enumerate(n):ax.text(i,v+max(n)*.02,f'{v}\n({100*v/len(d):.1f}%)',ha='center',fontsize=9)
    finish(fig,'01_group_counts')
    for c,label,unit,name,bins,color in [('MOCA_CLEAN','MoCA raw score','points','02_moca_hist',np.arange(-.5,31.5,1),COLORS[0]),(B,'Mean bilateral entorhinal thickness','mm','03_thickness_hist',np.linspace(np.floor(d[B].min()*2)/2,np.ceil(d[B].max()*2)/2,25),COLORS[2])]:
        fig,ax=plt.subplots(figsize=(8.4,3.5));ax.hist(d[c],bins=bins,color=color,edgecolor='white',linewidth=.6);ax.axvline(d[c].mean(),color='#222222',ls='--',lw=1.4,label=f'Mean = {d[c].mean():.2f}');ax.axvline(d[c].median(),color='#000000',lw=1.4,label=f'Median = {d[c].median():.2f}');ax.set_xlabel(f'{label} ({unit})');ax.set_ylabel('Participants (count)');ax.set_title(f'{label} | principal sample, N = {len(d)}');ax.legend(frameon=False)
        if c=='MOCA_CLEAN':ax.set_xlim(-.5,30.5)
        finish(fig,name)
    for c,label,unit,name in [('MOCA_CLEAN','MoCA raw score','points','04_moca_box'),(B,'Mean bilateral entorhinal thickness','mm','05_thickness_box')]:
        fig,ax=plt.subplots(figsize=(8.4,4.4));series=[d.loc[d.GROUP.eq(g),c].dropna() for g in GROUPS]
        bp=ax.boxplot(series,patch_artist=True,widths=.5,whis=1.5,flierprops={'marker':'o','markersize':3,'markerfacecolor':'none','markeredgecolor':'#555555'},medianprops={'color':'#111111','linewidth':1.6})
        for patch,col in zip(bp['boxes'],COLORS):patch.set_facecolor(col);patch.set_edgecolor('#111111');patch.set_alpha(1)
        for idx,line in enumerate(bp['medians']):
            line.set_color('#ffffff' if idx<2 else '#111111')
            line.set_linewidth(1.8)
        ax.set_xticks(np.arange(1,5),[f'{GROUPS[g]}\n(n = {len(s)})' for g,s in zip(GROUPS,series)],fontsize=9);ax.set_ylabel(f'{label} ({unit})');ax.set_title(f'{label} by cognitive status | N = {len(d)}')
        if c=='MOCA_CLEAN':ax.set_ylim(-1,31)
        else:ax.set_ylim(0,max(d[B])*1.07)
        finish(fig,name)
    manifest=[dict(figure=f'{i:02}',population='principal_joint',denominator=len(d),group_order='1,2,3,4',png=p.name,svg=p.with_suffix('.svg').name) for i,p in enumerate(sorted(p for p in (out/'figures').glob('*.png') if not p.name.endswith('.tmp.png')),1)]
    pd.DataFrame(manifest).to_csv(out/'tables'/'figure_denominators.csv',index=False)
