# فاز دوم پروژهٔ آمار — NACC UDS + MRI

آرام بقائی راد | شمارهٔ دانشجویی: ۴۰۳۱۰۰۰۷۶

این بسته شامل گزارش، کد، نوتبوک اجراشده، جدول‌ها، شکل‌ها و مستندات فاز دوم است.

| بخش | دسترسی |
| --- | --- |
| گزارش | [PDF فاز دوم](reports/phase2.pdf) · [HTML فاز دوم](reports/phase2.html) |
| نوتبوک | [نسخهٔ اجراشده](notebooks/phase2.html) · [فایل Jupyter](notebooks/phase2.ipynb) |
| الزامات | [پوشش ۱۴ تکلیف](docs/PHASE2_REQUIREMENT_COVERAGE.html) |
| روش و دفاع | [روش‌ها](docs/PHASE2_METHODS.html) · [مرور و دفاع](docs/PHASE2_STUDY_GUIDE.html) |
| اجرا و تحویل | [راهنما](docs/PHASE2_SUBMISSION.html) |
| کنترل کیفیت | [نتیجهٔ بررسی](docs/PHASE2_QA.html) |

## اجرای کامل

چهار فایل ورودی amarpr.pdf، udslong_imputed.csv، mriscanclean.csv و combined_adjacency_matrix.csv را در data/raw قرار دهید؛ پسوند بارگذاری مانند (9) پذیرفته می‌شود. دادهٔ خام مطابق دستورالعمل استاد داخل ZIP نیست.

```bash
python -m pip install -r requirements.txt
python src/phase2_analysis.py --data-dir data/raw --execute-notebook
python src/phase2_validate.py
```

Python 3.11 یا بالاتر و کتابخانه‌های متن Pango برای WeasyPrint لازم‌اند. برای مسیر ورودی دیگر، مقدار --data-dir را تغییر دهید. نوتبوک به ترتیب با اجرای واقعی سلول‌ها در IPython بازتولید می‌شود. متغیر NACC_DATA_DIR مسیر داده را برای اجرای دستی نوتبوک مشخص می‌کند. خروجی مستقل در پوشهٔ خالی با --out-dir قابل ساخت است.

گزارش فارسی با B Nazanin و قالب سیاه‌وسفید است. برچسب phase-2 در بستهٔ محلی Git موجود است؛ انتشار GitHub و ارسال CW در این جلسه انجام نشده‌اند.
