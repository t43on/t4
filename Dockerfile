# استخدم صورة Python رسمية خفيفة
FROM python:3.11-slim

# منع buffering عشان الـ logs تظهر فورًا
ENV PYTHONUNBUFFERED=1

# حدد مجلد العمل
WORKDIR /app

# نسخ requirements أولاً عشان cache
COPY requirements.txt .

# تثبيت الـ dependencies
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت gunicorn لو مش في requirements (للأمان)
RUN pip install gunicorn

# نسخ الكود
COPY app.py .

# البورت اللي Koyeb بيستخدمه (متغير بيئي)
EXPOSE 8000

# الأمر النهائي (استخدم exec و $PORT)
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --worker-class sync app:app
