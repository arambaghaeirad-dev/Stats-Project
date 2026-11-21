"""قرارداد مسیر و اثرانگشت ورودی‌های فاز دوم."""
from pathlib import Path
import re,hashlib

def resolve(data_dir,stem,ext):
    files=sorted(Path(data_dir).glob('*'+ext))
    candidates=[p for p in files if re.sub(r'\(\d+\)$','',re.sub(r'^\d+-','',p.stem))==stem]
    if len(candidates)!=1:
        raise ValueError(f'برای {stem}{ext} باید دقیقاً یک فایل موجود باشد: {[p.name for p in candidates]}')
    return candidates[0]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
