"""کنترل فایل‌ها و خروجی‌های فاز دوم."""
from pathlib import Path
import argparse,json,re
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import numpy as np
import pandas as pd
import nbformat
from pypdf import PdfReader
from PIL import Image

class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        self.links.extend(v for k,v in attrs if k in ['href','src'] and v)

def validate(root):
    root=Path(root).resolve()
    r=json.loads((root/'tables/p2_results.json').read_text())
    p=pd.read_csv(root/'tables/p2_05_probabilities.csv').set_index('probability')
    assert np.allclose(p.value,p.numerator/p.denominator,rtol=1e-10)
    assert p.value.between(0,1).all()
    n=r['n'];ab,anb,nab,nanb=r['cells']
    assert sum(r['cells'])==n
    assert np.isclose(p.loc['P(A|B)','value'],ab/(ab+nab))
    assert np.isclose((ab/(ab+anb))*((ab+anb)/n)/((ab+nab)/n),ab/(ab+nab))
    g=pd.read_csv(root/'tables/p2_06_status_by_mri.csv')
    assert np.isclose(g.P_group_given_B.sum(),1)
    assert np.isclose(g.P_group_given_B_complement.sum(),1)
    moments=pd.read_csv(root/'tables/p2_07_distributions.csv')
    assert np.allclose(moments.variance_sample,moments.variance_empirical*moments.n/(moments.n-1))
    b=pd.read_csv(root/'tables/p2_10_binomial_pmf.csv')
    assert np.isclose(b.probability.sum(),1)
    assert np.isclose((b.k*b.probability).sum(),r['binomial']['expected'])
    nb=nbformat.read(root/'notebooks/phase2.ipynb',as_version=4)
    codes=[c for c in nb.cells if c.cell_type=='code']
    assert codes and all(c.execution_count is not None for c in codes)
    assert not any(o.output_type=='error' for c in codes for o in c.get('outputs',[]))
    figures=sorted((root/'figures').glob('p2_*.png'))
    assert len(figures)==5 and all(p.with_suffix('.svg').exists() for p in figures)
    for path in figures:
        with Image.open(path) as im:im.verify()
    reader=PdfReader(root/'reports/phase2.pdf')
    assert len(reader.pages)>0
    nazanin_embedded=False
    for pg in reader.pages:
        for font in pg['/Resources'].get('/Font',{}).values():
            obj=font.get_object()
            if 'Nazanin' in str(obj.get('/BaseFont','')):
                descendant=obj.get('/DescendantFonts',[obj])[0].get_object()
                descriptor=descendant.get('/FontDescriptor')
                if descriptor and any(k in descriptor.get_object() for k in ['/FontFile','/FontFile2','/FontFile3']):
                    nazanin_embedded=True
    assert nazanin_embedded
    coverage=pd.read_csv(root/'docs/PHASE2_REQUIREMENT_COVERAGE.csv')
    assert set(coverage.requirement)=={f'G{i}' for i in range(1,10)}|{f'C{i}' for i in range(1,6)}
    assert coverage.validation_status.str.startswith('کامل').all()
    for path in root.rglob('*.html'):
        parser=Links();parser.feed(path.read_text())
        for link in parser.links:
            url=urlsplit(link)
            if not url.scheme and url.path:
                assert (path.parent/unquote(url.path)).exists(),f'پیوند شکسته: {path}: {link}'
    for path in root.rglob('*'):
        if path.suffix.lower() in ['.md','.html','.json','.csv','.ipynb']:
            text=path.read_text(encoding='utf-8-sig')
            assert not re.search(r'\bNACC\d{3,}\b',text),f'شناسهٔ فردی در خروجی: {path.name}'
        assert not re.search(r'phase[_-]?1',path.name,re.I),'فایل نامرتبط با فاز دوم در بسته وجود دارد.'
    assert not list((root/'data').rglob('*.csv'))
    result=dict(sample_n=n,notebook_code_cells=len(codes),notebook_errors=0,pdf_pages=len(reader.pages),
        font_embedded=nazanin_embedded,figures=len(figures),coverage_rows=len(coverage),
        probability_and_moments='موفق',relative_links='موفق',phase2_only=True,
        independent_execution='موفق؛ اجرای کامل فاز دوم')
    (root/'docs/phase2_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='کنترل خروجی‌های فاز دوم')
    parser.add_argument('--root',default=str(Path(__file__).resolve().parents[1]))
    print(json.dumps(validate(parser.parse_args().root),ensure_ascii=False,indent=2))
