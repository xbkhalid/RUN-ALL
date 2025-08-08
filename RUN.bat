@echo off

REM شغل Docker Desktop يدوياً قبل البدء!

REM تشغيل Qdrant (لو مو شغال) أو تجاهل لو يعمل
docker start qdrant 2>NUL || docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

REM تفعيل البيئة الافتراضية
call .\env\Scripts\activate

REM الذهاب إلى مجلد السكربتات
cd scripts

REM توليد الـ embeddings
python generate_embeddings.py

REM رفع البيانات إلى Qdrant
python upload_to_qdrant.py

REM الرجوع للمجلد الرئيسي
cd ..

REM تشغيل FastAPI عبر uvicorn في نافذة جديدة
start cmd /k ".\env\Scripts\python.exe -m uvicorn app.main:app --reload"

REM انتظر حتى يبدأ السيرفر فعلاً (نستخدم powershell لجلب كود الاستجابة)
echo انتظر قليلاً حتى يبدأ السيرفر...
:waitloop
powershell -Command "$r = try {Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/docs' -TimeoutSec 1} catch {''}; if ($r.StatusCode -eq 200) {exit 0} else {exit 1}"
if %errorlevel% neq 0 (
    timeout /t 2 > nul
    goto waitloop
)

REM فتح صفحة التوثيق تلقائياً بعد التأكد من عمل السيرفر
start http://127.0.0.1:8000/docs

echo تم تشغيل كل شيء بنجاح!
pause
