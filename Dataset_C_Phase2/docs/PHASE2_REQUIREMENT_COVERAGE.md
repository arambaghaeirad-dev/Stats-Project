# پوشش الزامات فاز دوم

مرجع: بخش ۶ راهنمای استاد، صفحات ۸ تا ۱۰. G به تکلیف مشترک و C به تکلیف مسیر ج اشاره می‌کند. شمارهٔ بخش مربوط به `reports/phase2.pdf` و عنوان سلول مربوط به `notebooks/phase2.ipynb` است.


| شماره | الزام | بخش گزارش | بخش کد / نوتبوک | خروجی | وضعیت |
| --- | --- | --- | --- | --- | --- |
| G1 | دو رویداد و متغیر تصادفی | ۴ | src/phase2_analysis.py: analyze: تعریف A، B و threshold؛ رویدادها و فضای احتمال | tables/p2_results.json | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| G2 | حاشیه و احتمال مشترک | ۵ | src/phase2_analysis.py: analyze: contingency و probabilities؛ احتمال حاشیه‌ای، مشترک و شرطی | tables/p2_04_contingency.csv | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| G3 | حداقل دو احتمال شرطی | ۶ | src/phase2_analysis.py: analyze: prob_rows و ratio؛ احتمال حاشیه‌ای، مشترک و شرطی | tables/p2_05_probabilities.csv | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| G4 | استقلال | ۶ | src/phase2_analysis.py: analyze: independence_product و difference؛ استقلال | figures/p2_01_conditional.png | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| G5 | گسسته و دوجمله‌ای | ۷ | src/phase2_analysis.py: analyze: binomial و binom؛ مدل شمارش دوجمله‌ای | tables/p2_10_binomial_pmf.csv | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| G6 | پیوسته و تقریب نرمال | ۸ | src/phase2_analysis.py: analyze: normal؛ phase2_plots.make_plots؛ توزیع دو سنجه و تقریب نرمال | figures/p2_02_mri_normal.png | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| G7 | امید و دو واریانس | ۱۰ | src/phase2_analysis.py: summary و کنترل ممان‌های PMF؛ امید و واریانس | tables/p2_07_distributions.csv | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| G8 | دو سنجه و کوواریانس | ۱۱ و ۱۱–۱ | src/phase2_analysis.py: covariance_row و تجزیهٔ within/between؛ کوواریانس | figures/p2_04_covariance.png | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| G9 | بیز | ۱۲ | src/phase2_analysis.py: analyze: هویت بیز و احتمال کل؛ بیز | tables/p2_05_probabilities.csv | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| C1 | وضعیت شناختی با شرط دو گروه MRI | ۵ و ۶ | src/phase2_analysis.py: analyze: status_cells و prob_rows؛ احتمال حاشیه‌ای، مشترک و شرطی | tables/p2_06_status_by_mri.csv | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| C2 | توزیع شناخت و MRI | ۸ و ۹ | src/phase2_analysis.py: summary؛ group_summaries؛ pmf؛ توزیع دو سنجه و تقریب نرمال | tables/p2_08_distributions_by_group.csv | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| C3 | احتمال مشترک UDS و MRI | ۴ تا ۶ | src/phase2_analysis.py: analyze: merge و contingency؛ احتمال حاشیه‌ای، مشترک و شرطی | tables/p2_04_contingency.csv | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| C4 | کوواریانس دو وجه | ۱۱ و ۱۱–۱ | src/phase2_analysis.py: covariance_row و independent_check؛ کوواریانس | tables/p2_11_covariance.csv | کامل؛ خروجی و اجرای نوتبوک کنترل شد |
| C5 | کنترل مراجعه‌های تکراری | ۲ و ۳ | src/phase2_analysis.py: analyze: یکتایی و validate=one_to_one؛ ساختار و مراجعه‌های تکراری | tables/p2_02_flow.csv | کامل؛ خروجی و اجرای نوتبوک کنترل شد |


## محدودیت‌های مستند

- **G1:** آستانهٔ چارکی اکتشافی است.
- **G2:** مخرج اصلی ثابت است.
- **G3:** مخرج صفر تعریف‌نشده ثبت می‌شود.
- **G4:** مقایسهٔ تجربی؛ بدون آزمون رسمی.
- **G5:** فرض استقلال و احتمال ثابت برای افراد فرضی است.
- **G6:** دنبالهٔ پایین با نرمال انحراف دارد.
- **G7:** مخرج‌های N و N−۱ تفکیک شده‌اند.
- **G8:** گروه کوچک برای تفسیر جداگانه کافی نیست.
- **G9:** احتمال تجربی؛ فاقد اعتبار تشخیصی.
- **C1:** گروه B و متمم B از MRI تعریف شده‌اند.
- **C2:** گمشدگی و IQR جدا ثبت شده‌اند.
- **C3:** A از UDS؛ B از MRI است.
- **C4:** بدون تفسیر علّی یا استنباط همبستگی.
- **C5:** یک رکورد موجود برای هر فرد؛ شمار تاریخی و انطباق زمانی نامعلوم.
