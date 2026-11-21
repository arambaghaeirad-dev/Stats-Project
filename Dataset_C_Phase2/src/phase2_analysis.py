"""فاز دوم: احتمال تجربی و توزیع‌های احتمالی در نمونهٔ تحلیل."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import platform
import shutil
import importlib.metadata

import numpy as np
import pandas as pd
from scipy import stats

from phase2_io import resolve, sha
from definitions import clean_uds, clean_mri, integer, GROUPS, FA_GROUPS, L, R, B

X = 'MOCA_CLEAN'
LABELS = {X: 'نمرهٔ MoCA', B: 'میانگین ضخامت انتورینال'}


def ratio(a, b):
    """مخرج صفر، احتمال تعریف‌نشده دارد؛ هرگز صفر ساختگی برنمی‌گردد."""
    return float(a / b) if b else float('nan')


def save_table(frame, root, name):
    frame.to_csv(Path(root) / 'tables' / ('p2_' + name + '.csv'),
                 index=False, encoding='utf-8-sig', float_format='%.12g')


def summary(series, base_n):
    x = series.dropna().to_numpy(dtype=float)
    n = len(x)
    if not n:
        raise ValueError('متغیر کمی هیچ مقدار معتبر ندارد.')
    q1, median, q3 = np.quantile(x, [.25, .5, .75], method='linear')
    lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    mean = float(np.mean(x))
    ss = float(np.sum((x - mean) ** 2))
    return dict(n=n, missing=base_n-n, mean=mean, sum=float(x.sum()),
                centered_ss=ss, variance_empirical=ss/n,
                variance_sample=ratio(ss, n-1), sd_empirical=math.sqrt(ss/n),
                skew=float(stats.skew(x, bias=False)) if n > 2 else float('nan'),
                q1=float(q1), median=float(median), q3=float(q3),
                min=float(x.min()), max=float(x.max()), lower_fence=float(lo),
                upper_fence=float(hi), low_outliers=int((x < lo).sum()),
                high_outliers=int((x > hi).sum()))


def covariance_row(d, label):
    z = d[[X, B]].dropna()
    x, y = z[X].to_numpy(), z[B].to_numpy()
    n = len(z)
    if n < 2:
        raise ValueError('برای کوواریانس حداقل دو مشاهدهٔ زوجی لازم است.')
    cross = float(np.sum((x-x.mean())*(y-y.mean())))
    return dict(group=label, n=n, mean_moca=float(x.mean()),
                mean_thickness=float(y.mean()), centered_cross_sum=cross,
                covariance_empirical=cross/n, covariance_sample=cross/(n-1))


def independent_check(files, threshold):
    """بازشماری مستقل با csv و math؛ بدون merge یا تابع پاک‌سازی pandas."""
    with files['udslong_imputed'].open(encoding='utf-8-sig', newline='') as f:
        uds = list(csv.DictReader(f))
    with files['mriscanclean'].open(encoding='utf-8-sig', newline='') as f:
        mr = list(csv.DictReader(f))
    mri = {row['NACCID']: row for row in mr}
    pairs, cells = [], [0, 0, 0, 0]
    for row in uds:
        if row['NACCID'] not in mri:
            continue
        g, x = float(row['NACCUDSD']), float(row['MOCATOTS'])
        rr = mri[row['NACCID']]
        left, right = float(rr[L]), float(rr[R])
        if (g not in GROUPS or not math.isfinite(x) or not 0 <= x <= 30
                or not math.isclose(x, round(x), abs_tol=1e-8, rel_tol=0)
                or not all(math.isfinite(t) and t > 0 for t in [left, right])):
            continue
        y = (left+right)/2
        pairs.append((x, y))
        cells[(0 if g == 4 else 2)+(0 if y <= threshold else 1)] += 1
    n = len(pairs)
    mx = math.fsum(x for x, _ in pairs)/n
    my = math.fsum(y for _, y in pairs)/n
    return dict(n=n, cells=cells, mean_moca=mx, mean_thickness=my,
                variance_moca=math.fsum((x-mx)**2 for x, _ in pairs)/n,
                variance_thickness=math.fsum((y-my)**2 for _, y in pairs)/n,
                covariance=math.fsum((x-mx)*(y-my) for x, y in pairs)/n)


def analyze(data_dir, root):
    root = Path(root).resolve()
    for folder in ['tables', 'figures', 'reports', 'docs', 'notebooks']:
        (root/folder).mkdir(parents=True, exist_ok=True)
    stems = ['udslong_imputed', 'mriscanclean', 'combined_adjacency_matrix', 'amarpr']
    files = {s: resolve(data_dir, s, '.pdf' if s == 'amarpr' else '.csv') for s in stems}
    u = pd.read_csv(files[stems[0]], dtype={'NACCID':'string'})
    m = pd.read_csv(files[stems[1]], dtype={'NACCID':'string'})
    a = pd.read_csv(files[stems[2]], index_col=0)
    for name, d, required in [('UDS', u, ['NACCID','NACCUDSD','MOCATOTS','NACCAGE','SEX','EDUC']),
                              ('MRI', m, ['NACCID','NACCUDSD',L,R])]:
        if not set(required) <= set(d):
            raise ValueError(f'{name}: ستون ضروری موجود نیست: {set(required)-set(d)}')
        if d.NACCID.isna().any() or not d.NACCID.is_unique:
            raise ValueError(f'{name}: شناسهٔ تهی یا تکراری؛ ابتدا قاعدهٔ مراجعه باید مشخص شود.')
        if not d.NACCID.str.fullmatch(r'NACC\d+').all():
            raise ValueError(f'{name}: قالب شناسه غیرمنتظره است.')
    uc, mc = clean_uds(u), clean_mri(m)
    joined = uc.merge(mc, on='NACCID', how='outer', suffixes=('_uds','_mri'),
                      indicator=True, validate='one_to_one')
    linked = joined[joined._merge.eq('both')].copy()
    linked['GROUP'] = linked.NACCUDSD_uds
    valid_status = linked.GROUP.isin(GROUPS)
    principal = linked[valid_status & linked.MOCA_VALID & linked[B].notna()].copy()
    if principal.empty:
        raise ValueError('نمونهٔ کامل با قواعد اعتبار تعیین‌شده خالی است.')
    n = len(principal)
    # آستانه فقط از MRI در نمونهٔ اصلی تحلیل؛ هیچ بهینه‌سازی نسبت به وضعیت انجام نمی‌شود.
    threshold = float(principal[B].quantile(.25, interpolation='linear'))
    A, BB = principal.GROUP.eq(4), principal[B].le(threshold)
    cells = [int((A&BB).sum()), int((A&~BB).sum()),
             int((~A&BB).sum()), int((~A&~BB).sum())]
    ab, anb, nab, nanb = cells
    na, nb = ab+anb, ab+nab
    pa, pb, pab = na/n, nb/n, ab/n
    prob_rows = [
        ('P(A)',na,n), ('P(B)',nb,n), ('P(A∩B)',ab,n),
        ('P(A∩Bᶜ)',anb,n), ('P(Aᶜ∩B)',nab,n), ('P(Aᶜ∩Bᶜ)',nanb,n),
        ('P(A|B)',ab,nb), ('P(A|Bᶜ)',anb,n-nb),
        ('P(B|A)',ab,na), ('P(B|Aᶜ)',nab,n-na)]
    probabilities = pd.DataFrame([dict(probability=k,numerator=c,denominator=d,value=ratio(c,d))
                                  for k,c,d in prob_rows])
    contingency = pd.DataFrame([
        dict(status='دمانس (A)', B=ab, B_complement=anb, total=na),
        dict(status='سایر وضعیت‌ها (متمم A)', B=nab, B_complement=nanb,total=n-na),
        dict(status='جمع', B=nb,B_complement=n-nb,total=n)])
    status_cells = []
    for g, label in FA_GROUPS.items():
        mask = principal.GROUP.eq(g)
        ng, low = int(mask.sum()), int((mask&BB).sum())
        status_cells.append(dict(group=g,label=label,n=ng,B=low,B_complement=ng-low,
                                 probability=ng/n, P_group_given_B=ratio(low,nb),
                                 P_group_given_B_complement=ratio(ng-low,n-nb)))
    group_table = pd.DataFrame(status_cells)
    summary_rows = []
    for pop, d in [('principal_joint',principal), ('linked_variable_available', linked[valid_status])]:
        for var in [X,B]:
            summary_rows.append(dict(population=pop,variable=var,label=LABELS[var],
                                     **summary(d[var],len(d))))
    summaries = pd.DataFrame(summary_rows)
    group_summaries = pd.DataFrame([dict(group=g,label=label,variable=var,
        **summary(principal.loc[principal.GROUP.eq(g),var], int(principal.GROUP.eq(g).sum())))
        for g,label in FA_GROUPS.items() for var in [X,B]])
    # توزیع احتمال تجربی متغیر گسسته در همهٔ نقاط ۰ تا ۳۰، حتی فراوانی صفر.
    score_freq = principal[X].value_counts().reindex(range(31),fill_value=0).sort_index()
    pmf = pd.DataFrame(dict(score=score_freq.index, count=score_freq.values,
                            probability=score_freq.values/n))
    pmf['cdf'] = pmf.probability.cumsum()
    cov_rows = [covariance_row(principal,'همهٔ افراد')]
    for g, label in FA_GROUPS.items():
        dg = principal[principal.GROUP.eq(g)]
        if len(dg) >= 20:
            cov_rows.append(covariance_row(dg,label))
    covariances = pd.DataFrame(cov_rows)
    mx, my = principal[X].mean(), principal[B].mean()
    within = between = 0.
    for g in GROUPS:
        dg = principal[principal.GROUP.eq(g)]
        if len(dg):
            cg = covariance_row(dg, str(g))
            within += len(dg)/n * cg['covariance_empirical']
            between += len(dg)/n * (dg[X].mean()-mx)*(dg[B].mean()-my)
    # مدل آموزشی شمار دمانس در ۱۰ فرد فرضی مستقل با احتمال ثابت برآوردشده.
    trials = 10
    k = np.arange(trials+1)
    binom = pd.DataFrame(dict(k=k, probability=stats.binom.pmf(k,trials,pa),
                              cdf=stats.binom.cdf(k,trials,pa)))
    binomial = dict(n=trials,p=pa,expected=trials*pa,variance=trials*pa*(1-pa),
                    p_exactly_2=float(stats.binom.pmf(2,trials,pa)),
                    p_at_least_1=float(stats.binom.sf(0,trials,pa)),
                    p_at_most_2=float(stats.binom.cdf(2,trials,pa)),
                    fraction_of_sample=trials/n)
    sy = summary(principal[B],n)
    # بازهٔ مرکزی خودِ داده؛ صرفاً مقایسهٔ احتمال تجربی با تقریب نرمال، نه CI میانگین.
    normal_lo, normal_hi = sy['mean']-sy['sd_empirical'], sy['mean']+sy['sd_empirical']
    normal_count = int(principal[B].between(normal_lo,normal_hi).sum())
    normal = dict(mu=sy['mean'],sigma=sy['sd_empirical'],lower=normal_lo,upper=normal_hi,
                  empirical_count=normal_count, empirical_probability=normal_count/n,
                  fitted_probability=float(stats.norm.cdf(1)-stats.norm.cdf(-1)),
                  p_below_threshold=float(stats.norm.cdf(threshold,sy['mean'],sy['sd_empirical'])),
                  p_negative=float(stats.norm.cdf(0,sy['mean'],sy['sd_empirical'])))
    flow = pd.DataFrame([
        ('رکورد خام UDS',len(u)),('فرد یکتای UDS',u.NACCID.nunique()),
        ('رکورد اضافی ناشی از شناسهٔ تکراری UDS',len(u)-u.NACCID.nunique()),
        ('رکورد خام MRI',len(m)),('فرد یکتای MRI',m.NACCID.nunique()),
        ('رکورد اضافی ناشی از شناسهٔ تکراری MRI',len(m)-m.NACCID.nunique()),
        ('پیوند مشترک',len(linked)),('فقط UDS',int(joined._merge.eq('left_only').sum())),
        ('فقط MRI',int(joined._merge.eq('right_only').sum())),
        ('اختلاف طبقهٔ UDS و MRI',int(linked.NACCUDSD_uds.ne(linked.NACCUDSD_mri).sum())),
        ('حذف مرحله‌ای: وضعیت نامعتبر',int((~valid_status).sum())),
        ('حذف مرحله‌ای: MoCA نامعتبر یا حل‌نشده',int((valid_status&~linked.MOCA_VALID).sum())),
        ('حذف مرحله‌ای: ضخامت ناموجود',int((valid_status&linked.MOCA_VALID&linked[B].isna()).sum())),
        ('نمونهٔ اصلی',n)],columns=['stage','n'])
    missing = pd.DataFrame([
        dict(stage='UDS پیش از اتصال',variable='MOCATOTS',total=len(u),explicit_na=int(u.MOCATOTS.isna().sum()),
             valid=int(uc.MOCA_VALID.sum()), unavailable=int((~uc.MOCA_VALID).sum())),
        dict(stage='MRI پیش از اتصال',variable=B,total=len(m),explicit_na=int(m[[L,R]].isna().any(axis=1).sum()),
             valid=int(mc[B].notna().sum()),unavailable=int(mc[B].isna().sum())),
        *[dict(stage='افراد پیوندی',variable=v,total=len(linked), explicit_na=int(linked['MOCATOTS'].isna().sum()) if v==X else int(linked[[L,R]].isna().any(axis=1).sum()),
               valid=int(linked[v].notna().sum()),unavailable=int(linked[v].isna().sum())) for v in [X,B]],
        *[dict(stage='نمونهٔ اصلی',variable=v,total=n,explicit_na=0,valid=n,unavailable=0) for v in [X,B]]])
    inventory = pd.DataFrame([dict(logical_name=s,file=p.name,sha256=sha(p),size_bytes=p.stat().st_size,
                                  rows=len(u) if s==stems[0] else len(m) if s==stems[1] else len(a) if s==stems[2] else None,
                                  columns=len(u.columns) if s==stems[0] else len(m.columns) if s==stems[1] else len(a.columns)+1 if s==stems[2] else None)
                              for s,p in files.items()])
    reference=json.loads((root/'docs/phase2_reference.json').read_text())
    for stem in stems[:3]:
        if inventory.set_index('logical_name').loc[stem,'sha256']!=reference['input_sha256'][stem]:
            raise ValueError('محتوای داده با ورودی مرجع متفاوت است؛ نسخهٔ ورودی را بررسی کنید.')
    assert n==reference['n']
    for var in [X,B]:
        now=summaries[(summaries.population=='principal_joint')&(summaries.variable==var)].iloc[0]
        assert np.isclose(now['mean'],reference['means'][var],atol=1e-6)
    independent = independent_check(files,threshold)
    assert independent['n']==n and independent['cells']==cells
    assert np.isclose(independent['covariance'],cov_rows[0]['covariance_empirical'])
    for var,key in [(X,'moca'),(B,'thickness')]:
        rr=summaries[(summaries.population=='principal_joint')&(summaries.variable==var)].iloc[0]
        assert np.isclose(independent['mean_'+key],rr['mean'])
        assert np.isclose(independent['variance_'+key],rr.variance_empirical)
        assert np.isclose(rr.variance_sample,rr.variance_empirical*n/(n-1))
    assert n==sum(cells) and principal.NACCID.is_unique
    assert len(set(u.NACCID)&set(m.NACCID))==len(linked)
    assert np.allclose(principal[B],(principal[L]+principal[R])/2)
    assert np.isclose(sum(c/n for c in cells),1)
    assert probabilities.value.dropna().between(0,1).all()
    assert np.isclose(ratio(ab,nb),ratio(ab,na)*pa/pb)
    assert np.isclose(pb,ratio(ab,na)*pa+ratio(nab,n-na)*(1-pa))
    assert np.isclose(pmf.probability.sum(),1) and np.isclose((pmf.score*pmf.probability).sum(),mx)
    assert np.isclose(binom.probability.sum(),1)
    assert np.allclose(binom.probability,[math.comb(trials,int(t))*pa**t*(1-pa)**(trials-t) for t in k])
    assert np.isclose((k*binom.probability).sum(),binomial['expected'])
    assert np.isclose(((k-binomial['expected'])**2*binom.probability).sum(),binomial['variance'])
    assert np.isclose(within+between,cov_rows[0]['covariance_empirical'])
    assert np.isclose(principal[[X,B]].cov().iloc[0,1],cov_rows[0]['covariance_sample'])
    assert math.isnan(ratio(1,0))
    adj = dict(shape=list(a.shape),symmetric=bool(np.array_equal(a.to_numpy(),a.to_numpy().T)),
               binary=bool(np.isin(a.to_numpy(),[0,1]).all()),labels_match=list(a.index)==list(a.columns),
               participant_key_present='NACCID' in a.columns)
    check_names=['یکتایی شناسه و اتصال یک‌به‌یک','مجموعهٔ شناسه‌ها و شمارش حذف‌ها','بازشماری مستقل جدول توافقی',
                 'بازتولید میانگین و واریانس با math و csv','تطبیق نمونه و نتایج مرجع',
                 'جمع احتمال‌ها و محدودهٔ صفر تا یک','هویت احتمال شرطی و بیز','جمع احتمال کل',
                 'ممان‌های توزیع تجربی MoCA','احتمال و ممان‌های دوجمله‌ای با فرمول ترکیبی',
                 'کوواریانس با NumPy و pandas و محاسبهٔ مستقل','تفکیک درون‌گروهی و بین‌گروهی',
                 'مخرج صفر','بدون تغییر ورودی‌ها']
    checks={key:'موفق' for key in check_names}
    checks['بدون تغییر ورودی‌ها']='موفق' if all(sha(p)==inventory.set_index('logical_name').loc[s,'sha256'] for s,p in files.items()) else 'ناموفق'
    payload=dict(n=n,linked=len(linked),threshold=threshold,cells=cells,na=na,nb=nb,pa=pa,pb=pb,pab=pab,
                 independence_product=pa*pb,independence_difference=pab-pa*pb,
                 conditional_difference=ratio(ab,nb)-ratio(anb,n-nb),
                 binomial=binomial,normal=normal,covariance=cov_rows[0],
                 within_covariance=within,between_covariance=between,adjacency=adj,
                 special_moca=int(uc.MOCA_SPECIAL.sum()),fractional_moca=int(uc.MOCA_FRACTIONAL.sum()),
                 out_of_range_moca=int((~uc.MOCA_INRANGE&~uc.MOCA_SPECIAL&uc.MOCATOTS.notna()).sum()),
                 checks=checks,independent_verification=independent)
    for name,frame in [('01_inputs',inventory),('02_flow',flow),('03_missingness',missing),
                       ('04_contingency',contingency),('05_probabilities',probabilities),
                       ('06_status_by_mri',group_table),('07_distributions',summaries),
                       ('08_distributions_by_group',group_summaries),('09_moca_pmf',pmf),
                       ('10_binomial_pmf',binom),('11_covariance',covariances)]:
        save_table(frame,root,name)
    availability=[]
    for group,label in FA_GROUPS.items():
        group_linked=linked[linked.GROUP.eq(group)]
        group_principal=principal[principal.GROUP.eq(group)]
        availability.append(dict(group=group,label=label,linked_n=len(group_linked),
            principal_n=len(group_principal),retained_percent=100*ratio(len(group_principal),len(group_linked)),
            special=int(group_linked.MOCA_SPECIAL.sum()),fractional=int(group_linked.MOCA_FRACTIONAL.sum()),
            out_of_range=int((~group_linked.MOCA_INRANGE&~group_linked.MOCA_SPECIAL).sum())))
    save_table(pd.DataFrame(availability),root,'13_availability_by_group')
    (root/'tables/p2_results.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    versions={v:importlib.metadata.version(v) for v in ['pandas','numpy','scipy','matplotlib','weasyprint','Markdown','nbformat','nbclient','ipykernel','IPython','pypdf','Pillow','arabic-reshaper','python-bidi']}
    (root/'docs/phase2_environment.json').write_text(json.dumps(dict(python=platform.python_version(),packages=versions),indent=2))
    return dict(principal=principal,linked=linked,results=payload,summaries=summaries,
                group_summaries=group_summaries,probabilities=probabilities,contingency=contingency,
                status_table=group_table,pmf=pmf,binomial_pmf=binom,covariances=covariances,
                flow=flow,missing=missing,inventory=inventory)


def main():
    parser=argparse.ArgumentParser(description='فاز دوم: احتمال و توزیع‌های احتمالی')
    parser.add_argument('--data-dir',default='data/raw')
    parser.add_argument('--out-dir',default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument('--execute-notebook',action='store_true')
    parser.add_argument('--skip-pdf',action='store_true')
    args=parser.parse_args()
    source=Path(__file__).resolve().parents[1]
    root=Path(args.out_dir).resolve()
    if root!=source:
        if root.exists() and any(root.iterdir()):
            raise ValueError('پوشهٔ خروجی مستقل باید خالی باشد.')
        shutil.copytree(source,root,dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__','.git','*.bundle','raw'))
    res=analyze(Path(args.data_dir).resolve(),root)
    from phase2_plots import make_plots
    from phase2_report import make_report
    from phase2_documentation import write_docs
    make_plots(res,root)
    make_report(res,root,pdf=not args.skip_pdf)
    if args.execute_notebook:
        from phase2_notebook import execute
        execute(root,args.data_dir)
    write_docs(res,root)
    print('فاز دوم اجرا شد؛ تعداد افراد نمونهٔ اصلی:',res['results']['n'])


if __name__=='__main__':
    main()
