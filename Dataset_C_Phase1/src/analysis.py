"""Read-only participant data; exported outputs are aggregates only."""
from pathlib import Path
import hashlib,json,platform,re
import numpy as np
import pandas as pd
from definitions import *

def resolve(data_dir,stem,ext):
    files=sorted(Path(data_dir).glob('*'+ext))
    candidates=[p for p in files if re.sub(r'\(\d+\)$','',re.sub(r'^\d+-','',p.stem))==stem]
    if len(candidates)!=1: raise ValueError(f'Expected exactly one {stem}{ext}; found {[p.name for p in candidates]}')
    return candidates[0]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(df,out,name): df.to_csv(out/'tables'/f'{name}.csv',index=False,encoding='utf-8-sig',float_format='%.8g')
def domain(c,columns):
    if c=='NACCID': return 'شناسه'
    idx=columns.index(c)
    ranges=[('SEX','NACCAGE','جمعیت‌شناختی'),('NACCFAM','NACCFFTD','سابقهٔ خانوادگی'),('ANYMEDS','PSYCDIS','سابقهٔ پزشکی و عوامل خطر'),('NACCAAAS','NACCVASD','دارو'),('HEIGHT','NORMEXAM','معاینه و اندازه‌گیری جسمی'),('NPIQINF','APPSEV','علائم عصب‌روان‌پزشکی'),('NOGDS','NACCGDS','خلق و افسردگی'),('BILLS','TRAVEL','عملکرد روزمره'),('DECSUB','MOCATOTS','شناختی'),('MEMORY','CDRGLOB','درجه‌بندی بالینی شناخت و عملکرد')]
    if c=='NACCAPOE': return 'ژنتیک'
    if c=='NACCUDSD': return 'وضعیت شناختی'
    for a,b,label in ranges:
        if columns.index(a)<=idx<=columns.index(b):return label
    return 'سایر؛ نیازمند فرهنگ اختصاصی'

def run(data_dir,out):
    out=Path(out);[ (out/p).mkdir(parents=True,exist_ok=True) for p in ['tables','figures','reports','docs'] ]
    files={s:resolve(data_dir,s,e) for s,e in [('udslong_imputed','.csv'),('mriscanclean','.csv'),('combined_adjacency_matrix','.csv'),('amarpr','.pdf')]}
    u=pd.read_csv(files['udslong_imputed'],dtype={'NACCID':'string'});m=pd.read_csv(files['mriscanclean'],dtype={'NACCID':'string'});a=pd.read_csv(files['combined_adjacency_matrix'],index_col=0)
    provenance=[dict(file=p.name,logical_name=s,size_bytes=p.stat().st_size,sha256=sha(p),rows=(len(u) if s=='udslong_imputed' else len(m) if s=='mriscanclean' else len(a) if s=='combined_adjacency_matrix' else None),columns=(len(u.columns) if s=='udslong_imputed' else len(m.columns) if s=='mriscanclean' else len(a.columns)+1 if s=='combined_adjacency_matrix' else None)) for s,p in files.items()]
    save(pd.DataFrame(provenance),out,'01_file_inventory')
    structure=[];record_dist=[];inventory=[]
    for name,d in [('UDS',u),('MRI',m)]:
        required=['NACCID','NACCUDSD']+(['MOCATOTS','NACCAGE','SEX','EDUC'] if name=='UDS' else [L,R]);assert set(required)<=set(d)
        structure.append(dict(modality=name,rows=len(d),unique_ids=d.NACCID.nunique(),missing_ids=d.NACCID.isna().sum(),duplicate_ids=d.NACCID.duplicated().sum(),exact_duplicate_rows=d.duplicated().sum(),visit_date_fields='none',scan_identifiers='none'))
        for k,v in d.groupby('NACCID').size().value_counts().sort_index().items():record_dist.append(dict(modality=name,records_per_id=k,participants=v))
        if d.NACCID.isna().any() or d.NACCID.duplicated().any():raise ValueError('Unresolved duplicate/missing IDs. No arbitrary visit selection allowed.')
        assert d.NACCID.str.fullmatch(r'NACC\d+').all(),'Unexpected identifier syntax'
        for c in d:
            s=pd.to_numeric(d[c],errors='coerce');parts=c.split('_')
            measure=parts[-1] if name=='MRI' and c.startswith(('LH_','RH_')) else ''
            inventory.append(dict(file=name,variable=c,dtype=str(d[c].dtype),domain=(domain(c,list(d)) if name=='UDS' else 'ناحیه‌ای MRI' if measure else 'شناسه' if c=='NACCID' else 'وضعیت شناختی'),hemisphere=parts[0] if measure else '',region='_'.join(parts[1:-1]) if measure else '',measurement=measure,unit=('mm' if measure=='AVGTH' else 'mm^3' if measure=='GVOL' else ''),definition_status=('S4؛ تطبیق نام، فرایند زیرمجموعه نامعلوم' if measure else 'نام دقیق حفظ شده؛ فرهنگ تفصیلی فقط برای متغیرهای منتخب'),explicit_na=d[c].isna().sum(),unique_values=d[c].nunique(),numeric_min=s.min(),numeric_max=s.max(),fractional_numeric=(np.isfinite(s)&~integer(s)).sum()))
    save(pd.DataFrame(structure),out,'03_structure');save(pd.DataFrame(record_dist),out,'03_record_count_distribution');save(pd.DataFrame(inventory),out,'02_all_variable_inventory')
    uc=clean_uds(u);mc=clean_mri(m)
    j=uc.merge(mc,on='NACCID',how='outer',suffixes=('_uds','_mri'),indicator=True,validate='one_to_one')
    linked=j.loc[j._merge.eq('both')].copy();linked['GROUP']=linked.NACCUDSD_uds
    disagreements=(linked.NACCUDSD_uds!=linked.NACCUDSD_mri).sum()
    # No silent reconciliation. UDS is the declared grouping source.
    valid_status=linked.NACCUDSD_uds.isin(GROUPS)
    principal=linked.loc[valid_status&linked.MOCA_VALID&linked[B].notna()].copy()
    extended=linked.loc[valid_status&linked.MOCA_INRANGE&linked[B].notna()].copy()
    counts={'uds_rows':len(u),'mri_rows':len(m),'uds_unique':u.NACCID.nunique(),'mri_unique':m.NACCID.nunique(),'shared':len(linked),'uds_only':sum(j._merge.eq('left_only')),'mri_only':sum(j._merge.eq('right_only')),'disagreement':int(disagreements),'selected':len(linked),'linked':len(linked),'principal':len(principal),'extended':len(extended),'special_moca':int(uc.MOCA_SPECIAL.sum()),'fractional_inrange':int(uc.MOCA_FRACTIONAL.sum()),'out_of_range_non_special':int((~uc.MOCA_INRANGE&~uc.MOCA_SPECIAL&uc.MOCATOTS.notna()).sum()),'educ99':int(u.EDUC.eq(99).sum())}
    flow=[]
    for label,num in [('UDS اولیه',len(u)),('MRI اولیه',len(m)),('افراد مشترک پس از انتخاب رکورد موجود',len(linked)),('فقط UDS',counts['uds_only']),('فقط MRI',counts['mri_only']),('اختلاف وضعیت شناختی دو فایل',disagreements),('حذف مرحله‌ای: وضعیت نامعتبر',sum(~valid_status)),('حذف مرحله‌ای: MoCA نامعتبر یا حل‌نشده',sum(valid_status&~linked.MOCA_VALID)),('حذف مرحله‌ای: ضخامت دوطرفه نامعتبر',sum(valid_status&linked.MOCA_VALID&linked[B].isna())),('نمونهٔ اصلی',len(principal)),('نمونهٔ تکمیلی مشروط با MoCA اعشاری داخل دامنه',len(extended))]:flow.append(dict(stage=label,n=num))
    save(pd.DataFrame(flow),out,'05_linkage_flow')
    audit=[];log=[]
    def auditrow(mod,c,raw,clean,rule):
        audit.append(dict(modality=mod,variable=c,total=len(raw),explicit_na=raw.isna().sum(),unavailable_after_rule=clean.isna().sum(),unavailable_pct=100*clean.isna().mean(),valid_n=clean.notna().sum(),rule=rule))
    for c,clean,rule in [('NACCUDSD',uc.NACCUDSD.where(uc.STATUS_VALID),'کدهای ۱،۲،۳،۴؛ بدون گردکردن'),('MOCATOTS',uc.MOCA_CLEAN,'عدد صحیح ۰ تا ۳۰؛ اعشاری حل‌نشده کنار گذاشته شده'),('NACCAGE',uc.AGE_CLEAN,'۱۸ تا ۱۲۰، متناهی'),('SEX',uc.SEX_CLEAN,'کدهای ۱ و ۲'),('EDUC',uc.EDUC_CLEAN,'سال صحیح ۰ تا ۳۶؛ ۹۹ نامعلوم')]:auditrow('UDS',c,u[c],clean,rule)
    for c in [L,R]:auditrow('MRI',c,m[c],mc[c+'_CLEAN'],'متناهی و مثبت؛ نقاط افراطی معتبر حفظ می‌شوند')
    auditrow('MRI',B,(m[L]+m[R])/2,mc[B],'میانگین فقط با دو نیمکرهٔ معتبر')
    save(pd.DataFrame(audit),out,'04_missingness')
    values=u.MOCATOTS.value_counts().sort_index().rename_axis('raw_value').reset_index(name='n')
    values['principal_allowed']=values.raw_value.between(0,30)&integer(values.raw_value)
    values['special_code']=values.raw_value.isin([88,-4])
    save(values,out,'04_moca_value_audit')
    def event(var,problem,mask,rule,evidence,action):log.append(dict(variable=var,problem=problem,values_affected=int(sum(mask)),participants_affected=int(sum(mask)),rule=rule,evidence=evidence,action=action))
    event('MOCATOTS','کد ویژه ۸۸ یا منفی ۴',uc.MOCA_SPECIAL,'تبدیل به ناموجود تحلیلی','S2/S3','exclude score')
    event('MOCATOTS','خارج از دامنه و غیرکد ویژه',~uc.MOCA_INRANGE&~uc.MOCA_SPECIAL&uc.MOCATOTS.notna(),'عدم برش به ۳۰؛ ناموجود','دامنه S2/S3؛ روش آماده‌سازی نامعلوم','exclude score')
    event('MOCATOTS','اعشاری داخل دامنه',uc.MOCA_FRACTIONAL,'بدون گردکردن؛ حذف از اصلی، حفظ در تکمیلی مشروط','جمع نمرهٔ خام ذاتاً گسسته؛ منشأ اعشار معلوم نیست','unresolved')
    event('EDUC','کد ۹۹',u.EDUC.eq(99),'ناموجود؛ بدون حذف فرد از سؤال اصلی','S2/S3','exclude education only')
    outlierrows=[]
    for pop,d in [('linked',linked),('principal',principal)]:
        for c in ['MOCA_CLEAN',B,L+'_CLEAN',R+'_CLEAN']:
            x=d[c].dropna();q1,q3=x.quantile([.25,.75],interpolation='linear');iqr=q3-q1;flag=(d[c]<q1-1.5*iqr)|(d[c]>q3+1.5*iqr)
            outlierrows.append(dict(population=pop,variable=c,valid_n=len(x),lower_fence=q1-1.5*iqr,upper_fence=q3+1.5*iqr,flagged_n=int(flag.sum()),action='review; retained'))
    for c in [L,R]:event(c,'اندازهٔ کمتر از ۱ mm برای بازبینی',mc[c+'_CLEAN'].lt(1),'حفظ؛ بدون تصویر و QC داوری قطعی ممکن نیست','پرچم محافظه‌کارانهٔ بازبینی، نه آستانهٔ حذف','retained')
    save(pd.DataFrame(log),out,'04_cleaning_log');save(pd.DataFrame(outlierrows),out,'04_iqr_review')
    freq=[]
    for pop,d in [('supplied',uc.rename(columns={'NACCUDSD':'GROUP'})),('principal',principal)]:
        for c,lab in [('GROUP',FA_GROUPS),('SEX_CLEAN',{1:'مرد (کد ۱)',2:'زن (کد ۲)'})]:
            for value,label in lab.items():
                n=int(d[c].eq(value).sum());freq.append(dict(population=pop,variable=c,code=value,label=label,n=n,denominator=len(d),percent=100*n/len(d)))
            if d[c].isna().any():freq.append(dict(population=pop,variable=c,code='',label='ناموجود',n=int(d[c].isna().sum()),denominator=len(d),percent=100*d[c].isna().mean()))
    save(pd.DataFrame(freq),out,'06_frequencies')
    overall=[];group=[]
    for pop,d,vars in [('linked_variable_available',linked,['MOCA_CLEAN',L+'_CLEAN',R+'_CLEAN',B,'AGE_CLEAN','EDUC_CLEAN']),('principal_joint',principal,['MOCA_CLEAN',L+'_CLEAN',R+'_CLEAN',B,'AGE_CLEAN','EDUC_CLEAN']),('extended_provisional',extended,['MOCATOTS',B])]:
        for c in vars:overall.append(dict(population=pop,variable=c,**summaries(d[c],len(d))))
        for g in GROUPS:
            dg=d.loc[d.GROUP.eq(g)]
            for c in vars:group.append(dict(population=pop,group=g,group_label=FA_GROUPS[g],variable=c,**summaries(dg[c],len(dg))))
    save(pd.DataFrame(overall),out,'07_overall');save(pd.DataFrame(group),out,'08_by_group')
    reasons=[]
    for g in GROUPS:
        d=linked.loc[linked.GROUP.eq(g)];p=principal.loc[principal.GROUP.eq(g)]
        reasons.append(dict(group=g,label=FA_GROUPS[g],linked_n=len(d),principal_n=len(p),retained_percent=100*len(p)/len(d),special=int(d.MOCA_SPECIAL.sum()),out_of_range=int((~d.MOCA_INRANGE&~d.MOCA_SPECIAL).sum()),fractional=int(d.MOCA_FRACTIONAL.sum())))
    save(pd.DataFrame(reasons),out,'05_availability_by_group')
    ecdf=[];shape=[]
    for c in ['MOCA_CLEAN',B]:
        x=principal[c].dropna();q1,q3=x.quantile([.25,.75]);n=len(x)
        shape.append(dict(variable=c,n=n,skew_descriptive=x.skew(),at_min=int(x.eq(x.min()).sum()),at_max=int(x.eq(x.max()).sum()),moca_at_zero=int(x.eq(0).sum()) if c=='MOCA_CLEAN' else None,moca_at_30=int(x.eq(30).sum()) if c=='MOCA_CLEAN' else None))
        for val,num in x.value_counts().sort_index().items():ecdf.append(dict(variable=c,value=val,n=num,percent=100*num/n))
    ec=pd.DataFrame(ecdf);ec['cumulative_percent']=ec.groupby('variable').percent.cumsum();save(ec,out,'06_empirical_distributions');save(pd.DataFrame(shape),out,'07_shape')
    ar=a.to_numpy();adj=dict(shape=list(a.shape),labels_match=list(a.index)==list(a.columns),binary=bool(np.isin(ar,[0,1]).all()),symmetric=bool(np.array_equal(ar,ar.T)),diagonal_ones=int(np.diag(ar).sum()),ones=int((ar==1).sum()),no_participant_key='NACCID' not in a.columns,documented_purpose='unknown; structural region matrix; excluded from participant merge')
    (out/'tables'/'adjacency_audit.json').write_text(json.dumps(adj,ensure_ascii=False,indent=2))
    # Independently reconcile sets, exclusions, and the derivation.
    assert len(set(u.NACCID)&set(m.NACCID))==len(linked)
    assert len(u)==counts['shared']+counts['uds_only']
    assert len(m)==counts['shared']+counts['mri_only']
    assert len(principal)==int((valid_status&linked.MOCA_VALID&linked[B].notna()).sum())
    assert principal.NACCID.is_unique and len(principal)>0
    assert np.allclose(principal[B],(principal[L]+principal[R])/2)
    assert principal[B].notna().all() and principal.MOCATOTS.between(0,30).all() and integer(principal.MOCATOTS).all()
    assert sum(x['principal_n'] for x in reasons)==len(principal)
    assert int(sum(valid_status&~linked.MOCA_VALID))+int(sum(valid_status&linked.MOCA_VALID&linked[B].isna()))+int(sum(~valid_status))+len(principal)==len(linked)
    assert all(sha(p)==r['sha256'] for (s,p),r in zip(files.items(),provenance)), 'Inputs changed'
    checks=dict(identifier_and_cardinality='passed',set_reconciliation='passed',exclusion_reconciliation='passed',bilateral_requires_both='passed',integer_moca_rule='passed',original_checksums_unchanged='passed',no_inference='descriptive pipeline only',python=platform.python_version(),pandas=pd.__version__,numpy=np.__version__)
    (out/'docs'/'qa_analysis.json').write_text(json.dumps(checks,indent=2))
    (out/'tables'/'counts.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2))
    return dict(u=u,m=m,linked=linked,principal=principal,extended=extended,counts=counts,adj=adj,provenance=provenance)
