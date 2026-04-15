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

    try:
        # Port 465 is for SSL (more secure and faster for Gmail)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_PASSWORD)
            smtp.send_message(msg)
        
        print(f"✅ OTP {otp} sent successfully to {receiver_email}")
        return otp
    except Exception as e:
        print(f"❌ Gmail SMTP Error: {e}")
        return None
