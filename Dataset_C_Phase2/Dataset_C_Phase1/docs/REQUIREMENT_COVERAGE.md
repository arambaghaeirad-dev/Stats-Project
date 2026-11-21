# پوشش الزامات

وضعیت‌ها به اجرای محلی اشاره دارند؛ تحویل بیرونی انجام نشده است.

| id | requirement | work_performed | report_section | supporting_file | status | limitation |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | منشأ و سازوکار | تفکیک NACC از زیرمجموعه و ذکر مجهولات | ۲ | docs/SOURCES.md | provisional | دوره و روش تهیهٔ زیرمجموعه معلوم نیست |
| T2 | واحد و ساختار | شمارش شناسه و رکورد؛ تاریخچه قابل بازیابی نیست | ۳ | tables/03_structure.csv | completed |  |
| T3 | نمونه‌گیری و تعمیم | مشاهده‌ای و غیرتصادفی؛ دامنهٔ تفسیر محدود | ۲ | PROJECT_CARD.md | completed |  |
| T4 | نوع و مقیاس متغیر | فرهنگ منتخب با نقش و واحد | ۴ | tables/02_selected_dictionary.csv | completed |  |
| T5 | ممیزی کیفیت | تهی، کد ویژه، اعشار، دامنه و تکرار | ۵ | tables/04_cleaning_log.csv | completed | عدم قطعیت آماده‌سازی مستند است |
| T6 | فراوانی و توزیع تجربی | تعداد، درصد، مخرج و توزیع تجمعی | ۷ | tables/06_empirical_distributions.csv | completed |  |
| T7 | مرکز و پراکندگی | تمام شاخص‌ها با n و ناموجود | ۸ | tables/07_overall.csv | completed |  |
| T8 | حداقل چهار شکل | پنج PNG و SVG با زیرنویس | ۷–۹ | tables/figure_denominators.csv | completed |  |
| T9 | مقایسهٔ توصیفی | دو سنجه در چهار گروه | ۹ | tables/08_by_group.csv | completed | گروه کوچک حفظ شده است |
| T10 | نهایی‌کردن سؤال | حفظ عبارت ثابت و تعریف جمعیت | ۱ و ۱۱ | PROJECT_CARD.md | completed |  |
| C1 | نقشهٔ دو وجه | موجودی همهٔ ستون‌ها و فرهنگ منتخب | ۳–۴ | tables/02_all_variable_inventory.csv | provisional | فرهنگ اختصاصی تحویل نشده؛ تعریف نام‌های منتخب با منبع عمومی تطبیق یافت |
| C2 | فرد و مراجعه | توزیع تعداد رکورد و قاعدهٔ توقف روی تکرار | ۳ | tables/03_record_count_distribution.csv | completed | تعداد تاریخی مراجعات قابل ارزیابی نیست |
| C3 | اتصال دو وجه | کنترل یک‌به‌یک، توافق کد و جریان افراد | ۶ | tables/05_linkage_flow.csv | provisional | کلید و قاعدهٔ زمانی اختصاصی در دسترس نیست |
| C4 | گمشدگی و انتخاب چندوجهی | ممیزی قبل و بعد؛ تصریح نبود فاقد MRI | ۵،۶ و ۱۰ | tables/04_missingness.csv | completed | مقایسهٔ MRI/بدون MRI قابل ارزیابی نیست |
| C5 | خلاصهٔ مشترک | MoCA و ضخامت با آمار و شکل | ۸–۱۰ | tables/08_by_group.csv | completed | تکمیلی اعشاری مشروط است |
| CARD1 | مسیر و زیرمجموعه | جزء جداگانه در کارت | ۱،۳،۴ و ۱۱ | PROJECT_CARD.md | completed |  |
| CARD2 | فایل‌های دقیق | جزء جداگانه در کارت | ۱،۳،۴ و ۱۱ | PROJECT_CARD.md | completed |  |
| CARD3 | عنوان خنثی | جزء جداگانه در کارت | ۱،۳،۴ و ۱۱ | PROJECT_CARD.md | completed |  |
| CARD4 | سؤال دقیق فارسی | جزء جداگانه در کارت | ۱،۳،۴ و ۱۱ | PROJECT_CARD.md | completed |  |
| CARD5 | واحد مشاهده | جزء جداگانه در کارت | ۱،۳،۴ و ۱۱ | PROJECT_CARD.md | completed |  |
| CARD6 | جمعیت قابل تفسیر | جزء جداگانه در کارت | ۱،۳،۴ و ۱۱ | PROJECT_CARD.md | completed |  |
| CARD7 | متغیر و مقیاس | جزء جداگانه در کارت | ۱،۳،۴ و ۱۱ | PROJECT_CARD.md | completed |  |
| CARD8 | نقش متغیرها | جزء جداگانه در کارت | ۱،۳،۴ و ۱۱ | PROJECT_CARD.md | completed |  |
| CARD9 | نوع سؤال | جزء جداگانه در کارت | ۱،۳،۴ و ۱۱ | PROJECT_CARD.md | completed |  |
| CARD10 | فرضیهٔ آزمون‌نشده | جزء جداگانه در کارت | ۱،۳،۴ و ۱۱ | PROJECT_CARD.md | completed |  |
| CARD11 | حداقل دو محدودیت | جزء جداگانه در کارت | ۱،۳،۴ و ۱۱ | PROJECT_CARD.md | completed |  |
| REPORT | گزارش فارسی قابل ویرایش و PDF | متن، جدول، شکل و منابع | ۱۲ / پیوست | reports/phase1.pdf | completed |  |
| CODE | کد ماژولار و محیط | اسکریپت‌ها و requirements | ۱۲ / پیوست | src/run.py | completed |  |
| NOTEBOOK | نوتبوک اجراشده | اجرا بدون خروجی شناسه فردی | ۱۲ / پیوست | notebooks/phase1_executed.ipynb | completed |  |
| REPRO | بازتولید و checksum | مسیر تنظیمی، قواعد و کنترل‌ها | ۱۲ / پیوست | README.md | completed |  |
| GITHUB | مخزن و تاریخچه واقعی | راهنما آماده؛ ارسال انجام نشده | ۱۲ / پیوست | docs/SUBMISSION_FA.md | not assessable from the supplied material | مخزن و دسترسی مشخص نشده است |
| TAG | برچسب phase-1 | دستور ساخت پس از بازبینی | ۱۲ / پیوست | docs/SUBMISSION_FA.md | not assessable from the supplied material | ساخته نشده است |
| CW | ZIP و ارسال CW | ZIP آماده؛ بارگذاری انجام نشده | ۱۲ / پیوست | docs/SUBMISSION_FA.md | provisional | کاربر باید ارسال کند |
| DEFENSE | راهنمای دفاع | توضیح مفاهیم و قواعد | ۱۲ / پیوست | docs/STUDY_GUIDE_FA.md | completed | دفاع واقعی و تسلط شخصی قابل ارزیابی نیست |
| C2HISTORY | تعداد مراجعات تاریخی | محدودیت صریح | ۱۲ / پیوست | tables/03_structure.csv | not assessable from the supplied material | تاریخ و شماره مراجعه موجود نیست |
| C4COMPARISON | مقایسهٔ با/بدون MRI | نبود گروه فاقد MRI مستند شد | ۱۲ / پیوست | tables/05_linkage_flow.csv | not assessable from the supplied material | همهٔ افراد UDS با MRI پیوند می‌یابند |

