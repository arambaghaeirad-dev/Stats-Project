"""Prespecified operational rules. No inference or automated rounding."""
import numpy as np
import pandas as pd
GROUPS = {1:'Normal cognition',2:'Impaired, not MCI',3:'MCI',4:'Dementia'}
FA_GROUPS = {1:'شناخت طبیعی',2:'اختلال شناختی، غیر MCI',3:'اختلال شناختی خفیف (MCI)',4:'دمانس'}
COLORS = ['#111111','#555555','#999999','#cccccc']
L='LH_ENTORHINAL_AVGTH'
R='RH_ENTORHINAL_AVGTH'
B='ENTORHINAL_BILATERAL_MEAN'
QUESTION='نمرهٔ MoCA و میانگین ضخامت قشر انتورینال در گروه‌های مختلف وضعیت شناختیِ شرکت‌کنندگان، چه توزیع و تفاوت‌های توصیفی دارند؟'
TITLE='توصیف نمرهٔ MoCA و ضخامت قشر انتورینال برحسب وضعیت شناختی در زیرمجموعهٔ NACC'
SOURCES = [
 ('S1','دستورالعمل رسمی درس آمار، پاییز ۱۴۰۵، amarpr.pdf؛ صفحات ۳ تا ۸ و ۱۸ تا ۲۰','فایل ارائه‌شده توسط تیم درس'),
 ('S2','NACC UDS Researcher’s Data Dictionary, v3.0 (March 2015), modified 8 April 2025؛ PDF pages 53,55,238,269','https://files.alz.washington.edu/documentation/uds3-rdd.pdf'),
 ('S3','NACC UDS Initial Visit Data Element Dictionary, v3.0, March 2015؛ Form A1 و C2','https://files.alz.washington.edu/documentation/uds3-ivp-ded.pdf'),
 ('S4','NACC SCAN & CLARiTI MRI Researcher’s Data Dictionary, April 2024؛ نسخهٔ در دسترس در تاریخ بررسی، صفحهٔ ۱۵؛ آخرین اصلاح درج‌شده 2026-09-18','https://files.alz.washington.edu/documentation/SCAN-MRI-Imaging-RDD.pdf'),
 ('S5','NACC: Longitudinal Neurocognitive and Clinical Phenotype Data','https://www.naccdata.org/about-nacc-data/longitudinal-neurocognitive-and-clinical-phenotype-data'),
 ('S6','NACC: Data Request Process و Data Use Agreement','https://www.naccdata.org/data-request-process'),
]
def numeric(s): return pd.to_numeric(s,errors='coerce')
def integer(s): return np.isfinite(s)&np.isclose(s,np.round(s),atol=1e-8,rtol=0)
def clean_uds(u):
    d=u.copy()
    for c in ['NACCUDSD','MOCATOTS','NACCAGE','SEX','EDUC']: d[c]=numeric(d[c])
    d['STATUS_VALID']=d.NACCUDSD.isin(GROUPS)
    d['MOCA_SPECIAL']=d.MOCATOTS.isin([88,-4])
    d['MOCA_INRANGE']=d.MOCATOTS.between(0,30)&np.isfinite(d.MOCATOTS)
    d['MOCA_FRACTIONAL']=d.MOCA_INRANGE&~integer(d.MOCATOTS)
    d['MOCA_VALID']=d.MOCA_INRANGE&integer(d.MOCATOTS)
    d['MOCA_CLEAN']=d.MOCATOTS.where(d.MOCA_VALID)
    d['EDUC_CLEAN']=d.EDUC.where(d.EDUC.between(0,36)&integer(d.EDUC))
    d['AGE_CLEAN']=d.NACCAGE.where(d.NACCAGE.between(18,120)&np.isfinite(d.NACCAGE))
    d['SEX_CLEAN']=d.SEX.where(d.SEX.isin([1,2]))
    return d

def clean_mri(m):
    d=m.copy()
    for c in [L,R]:
        s=numeric(d[c]); d[c+'_CLEAN']=s.where(np.isfinite(s)&(s>0))
    # addition propagates missingness: both hemispheres are required.
    d[B]=(d[L+'_CLEAN']+d[R+'_CLEAN'])/2
    return d

def summaries(s,base_n=None):
    s=numeric(s).dropna();n=len(s);q=s.quantile([.25,.75],interpolation='linear')
    return dict(n=n,missing=(base_n-n if base_n is not None else 0),mean=s.mean(),median=s.median(),sd=s.std(ddof=1),q1=q.loc[.25],q3=q.loc[.75],iqr=q.loc[.75]-q.loc[.25],min=s.min(),max=s.max())
