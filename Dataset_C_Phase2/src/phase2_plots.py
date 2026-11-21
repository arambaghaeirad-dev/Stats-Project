"""شکل‌های خاکستری فاز دوم با فونت و دارایی‌های اصلی پروژه."""
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager, ticker
import numpy as np
from scipy import stats
from definitions import FA_GROUPS, B
from phase2_analysis import X


def fa(text):
    return get_display(arabic_reshaper.reshape(str(text)))


def make_plots(res,root):
    root=Path(root)
    d,r=res['principal'],res['results']
    font_manager.fontManager.addfont(str(root/'assets/fonts/B-NAZANIN.TTF'))
    plt.rcParams.update({'font.family':['B Nazanin','DejaVu Sans'],'font.size':13,
        'axes.spines.top':False,'axes.spines.right':False,'axes.grid':False,
        'svg.fonttype':'path','axes.unicode_minus':False})
    manifest=[]
    def finish(fig,name,caption):
        fig.tight_layout(pad=1.5)
        fig.savefig(root/'figures'/f'{name}.png',dpi=280,bbox_inches='tight',facecolor='white')
        fig.savefig(root/'figures'/f'{name}.svg',bbox_inches='tight',facecolor='white')
        plt.close(fig)
        manifest.append(dict(figure=name,caption=caption,n=r['n'],population='principal_joint',
                             png=f'figures/{name}.png',svg=f'figures/{name}.svg'))
    vals=[r['cells'][0]/r['nb'],r['cells'][1]/(r['n']-r['nb'])]
    fig,ax=plt.subplots(figsize=(8.5,3.9))
    ax.bar([0,1],vals,color=['#555555','#bbbbbb'],edgecolor='black',width=.5)
    ax.axhline(r['pa'],ls='--',color='black',label=fa('احتمال حاشیه‌ای دمانس'))
    for i,v in enumerate(vals):
        num=r['cells'][i];den=r['nb'] if i==0 else r['n']-r['nb']
        ax.text(i,v+.012,fa(f'{num}/{den} = {v:.3f}'),ha='center',fontsize=13)
    ax.set_xticks([0,1],[fa('چارک پایین ضخامت (B)'),fa('بالاتر از آستانه (متمم B)')])
    ax.set_ylabel(fa('احتمال تجربی دمانس'))
    ax.set_ylim(0,max(vals)*1.35)
    ax.set_title(fa(f'وضعیت شناختی در دو گروه MRI؛ تعداد کل {r["n"]}'))
    ax.legend(frameon=False)
    finish(fig,'p2_01_conditional','احتمال شرطی دمانس در دو گروه ضخامت انتورینال')
    y=np.sort(d[B].to_numpy());mu,sig=r['normal']['mu'],r['normal']['sigma']
    fig,axes=plt.subplots(1,2,figsize=(10.2,4))
    ax=axes[0]
    ax.hist(y,bins=26,density=True,color='#bbbbbb',edgecolor='white',label=fa('چگالی تجربی'))
    grid=np.linspace(y.min()-.08,y.max()+.08,450)
    ax.plot(grid,stats.norm.pdf(grid,mu,sig),color='black',lw=1.7,label=fa('نرمال برازش‌شده'))
    ax.axvline(r['threshold'],color='#444444',ls='--',lw=1.2,label=fa('چارک اول'))
    ax.set_xlabel(fa('میانگین ضخامت انتورینال (میلی‌متر)'))
    ax.set_ylabel(fa('چگالی احتمال (معکوس میلی‌متر)'))
    ax.set_title(fa('توزیع پیوسته و تقریب نرمال'))
    ax.legend(frameon=False,fontsize=11)
    ax=axes[1]
    z=stats.norm.ppf((np.arange(1,len(y)+1)-.5)/len(y),loc=mu,scale=sig)
    ax.scatter(z,y,s=8,facecolors='none',edgecolors='#555555',linewidths=.55)
    bounds=[min(y.min(),z.min()),max(y.max(),z.max())]
    ax.plot(bounds,bounds,color='black',ls='--',lw=1)
    ax.set_xlabel(fa('چندک نرمال برازش‌شده (میلی‌متر)'))
    ax.set_ylabel(fa('چندک مشاهده‌شده (میلی‌متر)'))
    ax.set_title(fa('نمودار چندک–چندک ضخامت'))
    finish(fig,'p2_02_mri_normal','هیستوگرام چگالی ضخامت و چندک‌های آن در برابر نرمال')
    fig,axes=plt.subplots(1,2,figsize=(10.2,3.7))
    f=res['pmf'];axes[0].bar(f.score,f.probability,color='#555555',width=.85)
    axes[0].set_xlabel(fa('نمرهٔ MoCA (امتیاز)'));axes[0].set_ylabel(fa('جرم احتمال تجربی'))
    axes[0].set_title(fa('توزیع گسستهٔ MoCA'));axes[0].set_xlim(-.7,30.7)
    axes[1].step(f.score,f.cdf,where='post',color='black')
    axes[1].set_xlabel(fa('نمرهٔ MoCA (امتیاز)'));axes[1].set_ylabel(fa('احتمال تجمعی تجربی'))
    axes[1].set_ylim(0,1.04);axes[1].set_xlim(0,30)
    axes[1].set_title(fa('احتمال نمرهٔ کمتر یا مساوی مقدار محور'))
    finish(fig,'p2_03_moca_probability','تابع جرم و تابع توزیع تجمعی تجربی MoCA')
    fig,ax=plt.subplots(figsize=(8.7,4.8))
    colors=['#999999','#111111','#555555','#000000'];markers=['o','D','^','s']
    for (g,label),color,marker in zip(FA_GROUPS.items(),colors,markers):
        group=d[d.GROUP.eq(g)]
        ax.scatter(group[B],group[X],s=20 if g!=2 else 55,marker=marker,
                   facecolors='none' if g in [1,3] else color,edgecolors=color,
                   linewidths=.75,alpha=.65 if g!=2 else 1,label=fa(f'{label}؛ {len(group)} نفر'))
    ax.set_xlabel(fa('میانگین ضخامت انتورینال (میلی‌متر)'))
    ax.set_ylabel(fa('نمرهٔ MoCA (امتیاز)'));ax.set_ylim(-1,31)
    ax.set_title(fa(f'شناخت و تصویربرداری؛ {r["n"]} مشاهدهٔ زوجی'))
    ax.legend(frameon=False,fontsize=11,loc='lower right')
    finish(fig,'p2_04_covariance','نمودار پراکنش دو سنجه با تفکیک شکل و تیرگی گروه‌های شناختی')
    f=res['binomial_pmf'];fig,ax=plt.subplots(figsize=(8.5,3.5))
    ax.bar(f.k,f.probability,color='#777777',edgecolor='black',width=.65)
    ax.set_xticks(f.k);ax.set_xlabel(fa('تعداد افراد دارای وضعیت دمانس (K)'))
    ax.set_ylabel(fa('احتمال نظری'))
    ax.set_title(fa(f'مدل دوجمله‌ای آموزشی؛ n = 10 و p = {r["pa"]:.4f}'))
    finish(fig,'p2_05_binomial','جرم احتمال شمار دمانس در مدل آموزشی ده فرد فرضی')
    import pandas as pd
    pd.DataFrame(manifest).to_csv(root/'tables/p2_12_figure_manifest.csv',index=False,encoding='utf-8-sig')
