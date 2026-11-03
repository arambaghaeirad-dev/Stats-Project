from pathlib import Path
import argparse,shutil
from analysis import run
from plots import make_plots
from report import make_report
from documentation import write_docs

def main():
    parser=argparse.ArgumentParser(description='Phase 1 descriptive analysis only');parser.add_argument('--data-dir',default='data/raw');parser.add_argument('--out-dir',default=str(Path(__file__).resolve().parents[1]));parser.add_argument('--execute-notebook',action='store_true');parser.add_argument('--skip-pdf',action='store_true');a=parser.parse_args();out=Path(a.out_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    original=Path(__file__).resolve().parents[1]
    if out!=original:
        shutil.copytree(original/'src',out/'src',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(original/'assets',out/'assets',dirs_exist_ok=True)
        (out/'data').mkdir(exist_ok=True)
    result=run(a.data_dir,out);make_plots(result,out)
    if a.skip_pdf:
        import report
        saved=report.render_pdf;report.render_pdf=lambda _:None;make_report(result,out);report.render_pdf=saved
    else:make_report(result,out)
    write_docs(result,out)
    if a.execute_notebook:
        from execute_notebook import execute
        execute(out,a.data_dir)
    from typography import export_views
    export_views(out)
    print('Completed descriptive Phase 1:',result['counts'])
if __name__=='__main__':main()
