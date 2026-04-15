import smtplib
from email.message import EmailMessage

# CONFIGURATION
GMAIL_USER = "digitalbank93@gmail.com"
# PASTE THE 16-CHARACTER CODE HERE (DO NOT USE SPACES)
GMAIL_PASSWORD = "naiflulwjhpxqoli" 

def send_email(receiver_email, otp):
    if not otp:
        return None

    msg = EmailMessage()
    msg.set_content(f"Hello,\n\nYour Digital Bank OTP is: {otp}\n\nThis code will expire in 5 minutes. Do not share it with anyone.")
    msg["Subject"] = "Digital Bank OTP"
    msg["From"] = GMAIL_USER
    msg["To"] = receiver_email

import smtplib # Mela irukka-nu check pannikonga

# Intha logic use pannunga (Port 587 + STARTTLS)
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls() # Secure connection start pannum
    server.login("digitalbank93@gmail.com", "naiflulwjhpxqoli")
    server.send_message(msg)
    server.quit()
    print("✅ OTP sent via Port 587!")
except Exception as e:
    print(f"❌ SMTP 587 Error: {e}")
