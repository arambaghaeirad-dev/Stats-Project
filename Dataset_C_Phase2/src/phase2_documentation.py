"""مستندات بستهٔ مستقل فاز دوم."""
from pathlib import Path
import html
import json
import re
import markdown
import nbformat
import pandas as pd
from typography import font_css, BASE_CSS
from phase2_report import table, fmt


def view(path,root):
    path,root=Path(path),Path(root)
    body=markdown.markdown(path.read_text(),extensions=['tables','fenced_code'])
    css=font_css(root,path.parent)+BASE_CSS+'nav{padding:12px;border-bottom:1px solid #999}table{overflow-wrap:anywhere} @media(max-width:650px){body{font-size:17px;margin:15px auto;padding:0 12px}table{font-size:13px}}'
    path.with_suffix('.html').write_text('<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><title>'+html.escape(path.stem)+'</title><style>'+css+'</style></head><body>'+body+'</body></html>',encoding='utf-8')


def write_docs(res,root):
    root=Path(root);r=res['results']
    notebook=root/'notebooks/phase2.ipynb'
    executed=False
    if notebook.exists():
        nb=nbformat.read(notebook,as_version=4)
        codes=[c for c in nb.cells if c.cell_type=='code']
        executed=bool(codes) and all(c.get('execution_count') is not None for c in codes) and not any(o.output_type=='error' for c in codes for o in c.get('outputs',[]))
    requirements=[
        ('G1','دو رویداد و متغیر تصادفی','۴','analyze: تعریف A، B و threshold','رویدادها و فضای احتمال','tables/p2_results.json','آستانهٔ چارکی اکتشافی است.'),
        ('G2','حاشیه و احتمال مشترک','۵','analyze: contingency و probabilities','احتمال حاشیه‌ای، مشترک و شرطی','tables/p2_04_contingency.csv','مخرج اصلی ثابت است.'),
        ('G3','حداقل دو احتمال شرطی','۶','analyze: prob_rows و ratio','احتمال حاشیه‌ای، مشترک و شرطی','tables/p2_05_probabilities.csv','مخرج صفر تعریف‌نشده ثبت می‌شود.'),
        ('G4','استقلال','۶','analyze: independence_product و difference','استقلال','figures/p2_01_conditional.png','مقایسهٔ تجربی؛ بدون آزمون رسمی.'),
        ('G5','گسسته و دوجمله‌ای','۷','analyze: binomial و binom','مدل شمارش دوجمله‌ای','tables/p2_10_binomial_pmf.csv','فرض استقلال و احتمال ثابت برای افراد فرضی است.'),
        ('G6','پیوسته و تقریب نرمال','۸','analyze: normal؛ phase2_plots.make_plots','توزیع دو سنجه و تقریب نرمال','figures/p2_02_mri_normal.png','دنبالهٔ پایین با نرمال انحراف دارد.'),
        ('G7','امید و دو واریانس','۱۰','summary و کنترل ممان‌های PMF','امید و واریانس','tables/p2_07_distributions.csv','مخرج‌های N و N−۱ تفکیک شده‌اند.'),
        ('G8','دو سنجه و کوواریانس','۱۱ و ۱۱–۱','covariance_row و تجزیهٔ within/between','کوواریانس','figures/p2_04_covariance.png','گروه کوچک برای تفسیر جداگانه کافی نیست.'),
        ('G9','بیز','۱۲','analyze: هویت بیز و احتمال کل','بیز','tables/p2_05_probabilities.csv','احتمال تجربی؛ فاقد اعتبار تشخیصی.'),
        ('C1','وضعیت شناختی با شرط دو گروه MRI','۵ و ۶','analyze: status_cells و prob_rows','احتمال حاشیه‌ای، مشترک و شرطی','tables/p2_06_status_by_mri.csv','گروه B و متمم B از MRI تعریف شده‌اند.'),
        ('C2','توزیع شناخت و MRI','۸ و ۹','summary؛ group_summaries؛ pmf','توزیع دو سنجه و تقریب نرمال','tables/p2_08_distributions_by_group.csv','گمشدگی و IQR جدا ثبت شده‌اند.'),
        ('C3','احتمال مشترک UDS و MRI','۴ تا ۶','analyze: merge و contingency','احتمال حاشیه‌ای، مشترک و شرطی','tables/p2_04_contingency.csv','A از UDS؛ B از MRI است.'),
        ('C4','کوواریانس دو وجه','۱۱ و ۱۱–۱','covariance_row و independent_check','کوواریانس','tables/p2_11_covariance.csv','بدون تفسیر علّی یا استنباط همبستگی.'),
        ('C5','کنترل مراجعه‌های تکراری','۲ و ۳','analyze: یکتایی و validate=one_to_one','ساختار و مراجعه‌های تکراری','tables/p2_02_flow.csv','یک رکورد موجود برای هر فرد؛ شمار تاریخی و انطباق زمانی نامعلوم.')]
    rows=[]
    for code,desc,section,script,cell,output,note in requirements:
        generated=(root/output).is_file() and (root/'reports/phase2.pdf').is_file()
        status='کامل؛ خروجی و اجرای نوتبوک کنترل شد' if generated and executed else 'خروجی محاسبه شد؛ اجرای نوتبوک در انتظار کنترل'
        rows.append(dict(requirement=code,description=desc,report_section=section,
                         script='src/phase2_analysis.py: '+script,notebook_section=cell,
                         output=output,validation_status=status,limitation=note))
    df=pd.DataFrame(rows)
    df.to_csv(root/'docs/PHASE2_REQUIREMENT_COVERAGE.csv',index=False,encoding='utf-8-sig')
    coverage='''# پوشش الزامات فاز دوم

مرجع: بخش ۶ راهنمای استاد، صفحات ۸ تا ۱۰. G به تکلیف مشترک و C به تکلیف مسیر ج اشاره می‌کند. شمارهٔ بخش مربوط به `reports/phase2.pdf` و عنوان سلول مربوط به `notebooks/phase2.ipynb` است.

'''+table(['شماره','الزام','بخش گزارش','بخش کد / نوتبوک','خروجی','وضعیت'],[
        [row.requirement,row.description,row.report_section,row.script+'؛ '+row.notebook_section,row.output,row.validation_status]
        for row in df.itertuples()])
    coverage+='\n## محدودیت‌های مستند\n\n'+''.join(f'- **{row.requirement}:** {row.limitation}\n' for row in df.itertuples())
    (root/'docs/PHASE2_REQUIREMENT_COVERAGE.md').write_text(coverage)
    for path in [root/'README.md',root/'PROJECT_CARD.md',root/'data/README.md',*sorted((root/'docs').glob('*.md'))]:
        view(path,root)
