# استخدم Python 3.11 (أكثر استقرارًا من 3.13)
FROM python:3.11-slim

# حدد مجلد العمل
WORKDIR /app

# نسخ الملفات
COPY requirements.txt .
COPY app.py .

# تثبيت الـ dependencies (بما فيها gunicorn)
RUN pip install --no-cache-dir -r requirements.txt

# تأكد من تثبيت gunicorn لو مش في requirements
RUN pip install gunicorn

# حدد البورت اللي Koyeb بيستخدمه (متغير بيئي $PORT)
ENV PORT=8000

# الأمر اللي هيشتغل التطبيق
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 app:app
