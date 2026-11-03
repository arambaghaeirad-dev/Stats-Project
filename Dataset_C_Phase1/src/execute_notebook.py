from pathlib import Path
import os,argparse
import nbformat

def build_notebook(out):
    out=Path(out);(out/'notebooks').mkdir(exist_ok=True)
    md=nbformat.v4.new_markdown_cell;code=nbformat.v4.new_code_cell
    cells=[md('# فاز اول: شناخت داده و توصیف دو وجه\n\nاین نوتبوک زنجیرهٔ تحلیل توصیفی را با دادهٔ مجاز اجرا می‌کند. هیچ فایل فردی صادر نمی‌شود. اصل سؤال در PROJECT_CARD است؛ اعشار حل‌نشده با نمرهٔ صحیح اشتباه گرفته نمی‌شود.'),code('from pathlib import Path\nimport os, sys\nROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()\nsys.path.insert(0, str(ROOT / "src"))\nDATA_DIR = Path(os.environ.get("NACC_DATA_DIR", str(ROOT / "data" / "raw")))\nfrom analysis import run\nfrom definitions import *\nfrom IPython.display import display, Image\nimport pandas as pd\nresult = run(DATA_DIR, ROOT)\nprint("تحلیل توصیفی با موفقیت اجرا شد؛ شناسه‌های فردی نمایش داده نمی‌شوند.")'),md('## ساختار و اتصال\n\nتوزیع رکورد با تعداد مراجعات تاریخی فرق دارد. کلید تکراری یا ناموجود باعث توقف کد است. دو وضعیت شناختی مستقل حفظ و مقایسه می‌شوند.'),code('display(pd.read_csv(ROOT / "tables/03_structure.csv"))\ndisplay(pd.read_csv(ROOT / "tables/05_linkage_flow.csv"))'),md('## ممیزی و اعتبار\n\n۸۸ نمره نیست؛ ۹۹ تحصیلات نامعلوم است. MoCA اعشاری گرد نمی‌شود. میانگین MRI بدون دو نیمکرهٔ معتبر ساخته نمی‌شود.'),code('display(pd.read_csv(ROOT / "tables/04_missingness.csv"))\ndisplay(pd.read_csv(ROOT / "tables/04_cleaning_log.csv"))\ndisplay(pd.read_csv(ROOT / "tables/05_availability_by_group.csv"))'),md('## توصیف کمی و مقایسهٔ گروهی\n\nSD نمونه‌ای و چارک خطی است. جمعیت‌ها در ستون population جدا هستند؛ جدول مشروط با اصلی مخلوط نمی‌شود.'),code('overall = pd.read_csv(ROOT / "tables/07_overall.csv")\ngroups = pd.read_csv(ROOT / "tables/08_by_group.csv")\ndisplay(overall)\ndisplay(groups[(groups.population == "principal_joint") & groups.variable.isin(["MOCA_CLEAN", B])])'),md('## پنج شکل با مخرج مشترک\n\nبیرون شاخک، پرچم بازبینی است و خودکار حذف نشده است. همهٔ شکل‌ها از نمونهٔ اصلی مشترک استفاده می‌کنند.'),code('from plots import make_plots\nmake_plots(result, ROOT)\nfor name in ["01_group_counts", "02_moca_hist", "03_thickness_hist", "04_moca_box", "05_thickness_box"]:\n    display(Image(filename=str(ROOT / "figures" / (name + ".png")), width=760))'),md('## کنترل نهایی و تفسیر\n\nنتایج فقط توصیف نمونه‌اند؛ تعمیم جمعیتی، علیت یا تشخیص آلزایمر از MRI نتیجه نمی‌شود. نبود گروه بدون MRI و نامعلوم‌بودن آماده‌سازی محدودیت است.'),code('import json\nprint(json.dumps(json.loads((ROOT / "docs/qa_analysis.json").read_text()), ensure_ascii=False, indent=2))')]
    from typography import notebook_style
    cells.insert(0,md(notebook_style(out)))
    nb=nbformat.v4.new_notebook(cells=cells,metadata={'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'},'language_info':{'name':'python','version':sys_version()}})
    path=out/'notebooks'/'phase1_executed.ipynb';nbformat.write(nb,path);return path

def sys_version():
    import platform
    return platform.python_version()
def execute(out,data_dir):
    out=Path(out).resolve();path=build_notebook(out);os.environ['NACC_DATA_DIR']=str(Path(data_dir).resolve())
    # Execute the actual notebook cells in one IPython namespace. This avoids
    # sockets in restricted hosts; outputs are captured, never fabricated.
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output
    shell=InteractiveShell.instance()
    nb=nbformat.read(path,as_version=4)
    old_cwd=Path.cwd()
    try:
        os.chdir(out)
        count=0
        for cell in nb.cells:
            if cell.cell_type!='code':continue
            count+=1
            with capture_output() as captured:
                result=shell.run_cell(cell.source,store_history=True)
            if result.error_before_exec or result.error_in_exec:
                raise RuntimeError(f'Notebook cell {count} failed') from (result.error_before_exec or result.error_in_exec)
            outputs=[]
            if captured.stdout:outputs.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
            if captured.stderr:outputs.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
            for item in captured.outputs:
                outputs.append(nbformat.v4.new_output('display_data',data=item.data,metadata=item.metadata))
            cell.outputs=outputs
            cell.execution_count=count
        nb.metadata['execution_method']='Sequential actual execution with IPython InteractiveShell; in-process, no network sockets'
        nbformat.write(nb,path)
    finally:os.chdir(old_cwd)
    assert all(o.output_type!='error' for c in nb.cells if c.cell_type=='code' for o in c.outputs)
    from typography import export_views
    export_views(out)
    return path
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data-dir',required=True);p.add_argument('--out-dir',default=str(Path(__file__).resolve().parents[1]));a=p.parse_args();print(execute(a.out_dir,a.data_dir))
