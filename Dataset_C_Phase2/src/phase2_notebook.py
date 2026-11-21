"""ساخت و اجرای واقعی و متوالی سلول‌های فاز دوم در IPython."""
from pathlib import Path
import os
import html
import nbformat
import markdown
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from typography import notebook_style, font_css, BASE_CSS


def build(root):
    root=Path(root).resolve()
    md,code=nbformat.v4.new_markdown_cell,nbformat.v4.new_code_cell
    cells=[md(notebook_style(root)),md('''# فاز دوم: احتمال و توزیع‌های شناخت و تصویربرداری

نام: آرام بقائی راد | شمارهٔ دانشجویی: ۴۰۳۱۰۰۰۷۶

این نوتبوک تحلیل احتمال و توزیع‌های احتمالیِ سنجه‌های شناختی و تصویربرداری را اجرا می‌کند. احتمال‌ها متعلق به توزیع تجربی همین افرادند و شیوع جمعیتی نیستند. اجرای متوالی سلول‌ها فقط خروجی‌های فاز دوم را بازتولید می‌کند.'''),code('''from pathlib import Path
import os, sys
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents]
            if (p / 'src' / 'phase2_analysis.py').is_file())
sys.path.insert(0, str(ROOT / 'src'))
DATA_DIR = Path(os.environ.get('NACC_DATA_DIR', str(ROOT / 'data' / 'raw')))
from phase2_analysis import analyze, X, B
from phase2_plots import make_plots
from IPython.display import display, Image
import numpy as np
import pandas as pd
result = analyze(DATA_DIR, ROOT)
r = result['results']
labels = {'stage':'مرحله','n':'تعداد','variable':'متغیر','label':'گروه',
 'population':'جمعیت','mean':'میانگین','variance_empirical':'واریانس تجربی',
 'variance_sample':'واریانس نمونه‌ای','skew':'چولگی','min':'کمینه','max':'بیشینه',
 'low_outliers':'دورافتادهٔ پایین','high_outliers':'دورافتادهٔ بالا','missing':'ناموجود',
 'probability':'احتمال','numerator':'صورت','denominator':'مخرج','value':'مقدار',
 'status':'وضعیت شناختی','B':'چارک پایین','B_complement':'بالاتر از آستانه','total':'جمع',
 'k':'شمار K','cdf':'احتمال تجمعی','covariance_empirical':'کوواریانس تجربی',
 'covariance_sample':'کوواریانس نمونه‌ای','group':'گروه'}
def show(frame):
    frame=frame.copy()
    if 'population' in frame:
        frame['population']=frame.population.replace({'principal_joint':'نمونهٔ اصلی',
                   'linked_variable_available':'دسترسی متغیر در افراد پیوندی'})
    if 'variable' in frame:
        frame['variable']=frame.variable.replace({X:'نمرهٔ MoCA',B:'ضخامت انتورینال'})
    display(frame.rename(columns=labels))
print('تعداد افراد نمونهٔ اصلی:', r['n'])'''),md('''## ساختار و مراجعه‌های تکراری — مسیر ج، تکلیف ۵

کلید اتصال NACCID است. هر شناسه تنها یک رکورد آماده در هر وجه دارد؛ همان رکورد حفظ می‌شود. فقدان شماره و تاریخ مراجعه مانع بازیابی تاریخچه است. صفر رکورد تکراری در این فایل با صفر مراجعهٔ تاریخی فرق دارد. کد در صورت تکرار شناسه متوقف می‌شود.'''),code('''show(result['flow'])
show(result['missing'])
print('ابعاد ماتریس ناحیه‌ای؛ وارد اتصال فردی نشده:', r['adjacency']['shape'])'''),md('''## رویدادها و فضای احتمال — تکلیف مشترک ۱

Ω مجموعهٔ افراد نمونهٔ اصلی است؛ هر فرد وزن یک بر N دارد. A وضعیت دمانس با NACCUDSD=4 در UDS است. B ضخامت کمتر یا مساوی چارک اول در همین نمونه است؛ حد اکتشافی و غیرتشخیصی است. X نمرهٔ MoCA و Y میانگین ضخامت دو نیمکره‌اند. افراد فاقد اعتبار سنجه‌ها قبل از تشکیل Ω کنار گذاشته می‌شوند، نه اینکه در متمم رویداد قرار گیرند.'''),code('''d = result['principal']
A = d.GROUP.eq(4)
B_event = d[B].le(r['threshold'])
print('آستانهٔ چارک اول، میلی‌متر:', r['threshold'])
print('تعداد A، تعداد B و تعداد مشترک:', int(A.sum()), int(B_event.sum()), int((A & B_event).sum()))
assert d.NACCID.is_unique and d[[X,B]].notna().all().all()'''),md('''## احتمال حاشیه‌ای، مشترک و شرطی — مشترک ۲ و ۳؛ مسیر ج، ۱ و ۳

احتمال حاشیه‌ای و مشترک با مخرج کل نمونه است. در احتمال A با شرط B، مخرج فقط افراد B است. دو گروه MRI شامل چارک پایین و بالاتر از آستانه‌اند. طبقه‌بندی چهارگانهٔ UDS برای نمایش کامل نیز حفظ شده است.'''),code('''show(result['contingency'])
show(result['probabilities'])
show(result['status_table'][['label','n','B','B_complement']])
print('تفاوت احتمال دمانس بین دو گروه، واحد درصد:', 100*r['conditional_difference'])'''),md('''## استقلال — تکلیف مشترک ۴

در توزیع تجربی، برابری احتمال مشترک و حاصل‌ضرب حاشیه‌ها شرط استقلال است. این مقایسه آزمون فرض جمعیتی نیست و برابری تقریبی نیز استقلال جمعیتی را ثابت نمی‌کند.'''),code('''show(pd.DataFrame({'کمیت':['احتمال مشترک','حاصل‌ضرب حاشیه‌ها','اختلاف'],
                   'مقدار':[r['pab'],r['independence_product'],r['independence_difference']]}))
make_plots(result, ROOT)
display(Image(filename=str(ROOT/'figures/p2_01_conditional.png'), width=800))'''),md('''## مدل شمارش دوجمله‌ای — تکلیف مشترک ۵

K شمار دمانس در ده فرد فرضی با احتمال ثابت p برابر نسبت تجربی A است. تعداد ثابت، پیامد دودویی، استقلال و احتمال یکسان فرض‌های مدل‌اند. یکتایی شناسه تنها از تکرار فرد جلوگیری می‌کند؛ تفاوت خطر گروهی و وابستگی مرکز و خانواده معلوم نیست. مدل آموزشی و تقریبی است؛ انتخاب بدون جایگذاری از مجموعهٔ محدود دقیقاً دوجمله‌ای نیست.'''),code('''import math
from scipy.stats import binom
bn=r['binomial']
show(result['binomial_pmf'])
show(pd.DataFrame({'کمیت':['دقیقاً دو نفر','حداقل یک نفر','حداکثر دو نفر','امید','واریانس'],
 'مقدار':[bn['p_exactly_2'],bn['p_at_least_1'],bn['p_at_most_2'],bn['expected'],bn['variance']]}))
assert np.isclose(bn['p_exactly_2'], math.comb(10,2)*bn['p']**2*(1-bn['p'])**8)
display(Image(filename=str(ROOT/'figures/p2_05_binomial.png'), width=800))'''),md('''## توزیع دو سنجه و تقریب نرمال — مشترک ۶؛ مسیر ج، ۲

MoCA گسسته، محدود و چوله است؛ تابع جرم تجربی مبناست. ضخامت پیوسته مدل می‌شود. منحنی نرمال با میانگین و انحراف معیار تجربی برازش می‌شود؛ چندک‌ها با احتمال (i−۰٫۵)/N محاسبه شده‌اند. خط برابری در نمودار چندک‌ها رگرسیون نیست. نقاط IQR برای بازبینی حفظ می‌شوند.'''),code('''show(result['summaries'][['population','variable','n','missing','mean','variance_empirical',
 'variance_sample','skew','min','max','low_outliers','high_outliers']])
show(result['group_summaries'][['label','variable','n','mean','variance_empirical','skew']])
for name in ['p2_02_mri_normal','p2_03_moca_probability']:
    display(Image(filename=str(ROOT/'figures'/f'{name}.png'), width=900))
normal=r['normal']
print('احتمال تجربی بازهٔ میانگین ± انحراف معیار:',normal['empirical_probability'])
print('احتمال همان بازه در نرمال:',normal['fitted_probability'])'''),md('''## امید و واریانس — تکلیف مشترک ۷

امید تجربی برابر جمع مقدار ضرب‌در فراوانی نسبی و برابر میانگین نمونه است. واریانس تجربی مخرج N و واریانس نمونه‌ای مخرج N−۱ دارد؛ دومی تحت فرض‌های نمونه‌گیری مستقل و هم‌توزیع تصحیح نااریبی دارد. نام «نمونه‌ای» به‌تنهایی نمایندگی جمعیت را ایجاد نمی‌کند.'''),code('''pmf=result['pmf']
expectation=(pmf.score*pmf.probability).sum()
variance=((pmf.score-expectation)**2*pmf.probability).sum()
assert np.isclose(expectation,d[X].mean())
assert np.isclose(variance,d[X].var(ddof=0))
assert np.isclose(d[X].var(ddof=1),variance*len(d)/(len(d)-1))
show(pd.DataFrame({'متغیر':['MoCA','ضخامت','شمار دوجمله‌ای'],
 'امید':[expectation,d[B].mean(),bn['expected']],
 'واریانس تجربی یا نظری':[variance,d[B].var(ddof=0),bn['variance']],
 'واریانس نمونه‌ای':[d[X].var(ddof=1),d[B].var(ddof=1),np.nan]}))'''),md('''## کوواریانس — مشترک ۸؛ مسیر ج، ۴

تنها زوج‌های کامل همان افراد استفاده می‌شوند. واحد کوواریانس امتیاز×میلی‌متر است. جهت مثبت رابطهٔ کلی با سهم ترکیب گروه‌ها همراه است و علت یا شیب تغییر نیست. گروه چهارنفری برای تفسیر کوواریانس جداگانه کافی نیست؛ در محاسبهٔ کلی حفظ شده است.'''),code('''show(result['covariances'][['group','n','covariance_empirical','covariance_sample']])
assert np.isclose(np.cov(d[X],d[B],ddof=1)[0,1],r['covariance']['covariance_sample'])
print('جزء درون‌گروهی وزنی:',r['within_covariance'])
print('جزء تفاوت میانگین گروه‌ها:',r['between_covariance'])
assert np.isclose(r['within_covariance']+r['between_covariance'],r['covariance']['covariance_empirical'])
display(Image(filename=str(ROOT/'figures/p2_04_covariance.png'), width=850))'''),md('''## بیز — تکلیف مشترک ۹

پیشین، احتمال A قبل از دانستن گروه MRI است؛ احتمال شواهد، احتمال B در A است؛ پسین، احتمال A پس از دانستن B است. آستانهٔ چارکی اعتبار آزمون تشخیصی ندارد. این محاسبه دربارهٔ فرد انتخاب‌شده از همین فضای نمونه است، نه احتمال پارامتر ناشناخته.'''),code('''prior=A.mean()
likelihood=B_event[A].mean()
evidence=B_event.mean()
posterior=likelihood*prior/evidence
direct=A[B_event].mean()
assert np.isclose(posterior,direct)
show(pd.DataFrame({'جزء':['پیشین','احتمال شواهد در A','احتمال حاشیه‌ای شواهد','پسین بیز','بازشماری مستقیم'],
                   'مقدار':[prior,likelihood,evidence,posterior,direct]}))'''),md('''## کنترل نهایی و ساخت گزارش

کنترل عددی مستقل، با csv و math، در زنجیرهٔ اصلی اجرا شده است. گزارش از همان خروجی محاسبات ساخته می‌شود؛ دادهٔ فردی صادر نمی‌شود. مجهولاتِ جایگذاری، تاریخچه و انطباق زمانی، با ادعای تکمیل فراداده پوشانده نمی‌شوند.'''),code('''from phase2_report import make_report
make_report(result,ROOT)
show(pd.DataFrame(list(r['checks'].items()),columns=['کنترل','وضعیت']))
assert all(status=='موفق' for status in r['checks'].values())
assert (ROOT/'reports/phase2.pdf').is_file()
print('گزارش فارسی و کنترل‌های عددی ساخته و اجرا شدند.')''')]
    nb=nbformat.v4.new_notebook(cells=cells,metadata={
        'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'},
        'language_info':{'name':'python'},'title':'فاز دوم: احتمال'})
    path=root/'notebooks/phase2.ipynb'
    nbformat.write(nb,path)
    return path


def export_html(path,root):
    path,root=Path(path),Path(root)
    nb=nbformat.read(path,as_version=4)
    parts=[]
    for cell in nb.cells:
        if cell.cell_type=='markdown':
            parts.append(markdown.markdown(cell.source,extensions=['tables','fenced_code']))
        else:
            parts.append('<pre dir="ltr"><code>'+html.escape(cell.source)+'</code></pre>')
            for out in cell.get('outputs',[]):
                if out.output_type=='stream':
                    parts.append('<pre>'+html.escape(out.text)+'</pre>')
                elif out.output_type in ['display_data','execute_result']:
                    data=out.data
                    if 'image/png' in data:
                        parts.append('<img alt="نمودار فاز دوم" src="data:image/png;base64,'+data['image/png']+'">')
                    elif 'text/html' in data:
                        parts.append(data['text/html'])
                    elif 'text/plain' in data:
                        parts.append('<pre>'+html.escape(data['text/plain'])+'</pre>')
    css=font_css(root,path.parent,True)+BASE_CSS+'pre{font-family:monospace;font-size:13px}table{text-align:right!important}.dataframe{direction:rtl}img{display:block;margin:20px auto}'
    path.with_suffix('.html').write_text('<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><title>نوتبوک اجراشدهٔ فاز دوم</title><style>'+css+'</style></head><body>'+''.join(parts)+'</body></html>',encoding='utf-8')


def execute(root,data_dir):
    root=Path(root).resolve()
    path=build(root)
    previous=os.environ.get('NACC_DATA_DIR')
    os.environ['NACC_DATA_DIR']=str(Path(data_dir).resolve())
    try:
        nb=nbformat.read(path,as_version=4)
        shell=InteractiveShell.instance()
        previous_cwd=Path.cwd()
        try:
            os.chdir(root/'notebooks')
            execution_count=0
            for cell in nb.cells:
                if cell.cell_type!='code':
                    continue
                execution_count+=1
                with capture_output() as captured:
                    outcome=shell.run_cell(cell.source,store_history=True)
                if outcome.error_before_exec or outcome.error_in_exec:
                    raise RuntimeError(f'خطا در سلول {execution_count}') from (outcome.error_before_exec or outcome.error_in_exec)
                outputs=[]
                if captured.stdout:
                    outputs.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
                if captured.stderr:
                    outputs.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
                for item in captured.outputs:
                    outputs.append(nbformat.v4.new_output('display_data',data=item.data,metadata=item.metadata))
                cell.outputs=outputs
                cell.execution_count=execution_count
        finally:
            os.chdir(previous_cwd)
        assert all(c.execution_count is not None for c in nb.cells if c.cell_type=='code')
        assert not any(o.output_type=='error' for c in nb.cells for o in c.get('outputs',[]))
        nb.metadata['execution_method']='اجرای واقعی و متوالی همهٔ سلول‌ها در IPython InteractiveShell، درون فرایند و بدون سوکت'
        nbformat.write(nb,path)
        export_html(path,root)
    finally:
        if previous is None:
            os.environ.pop('NACC_DATA_DIR',None)
        else:
            os.environ['NACC_DATA_DIR']=previous
    return path
