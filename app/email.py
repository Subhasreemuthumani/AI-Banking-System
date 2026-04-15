import smtplib
from email.message import EmailMessage

# CONFIGURATION
GMAIL_USER = "digitalbank93@gmail.com"
GMAIL_PASSWORD = "naiflulwjhpxqoli" 

def send_email(receiver_email, otp):
    if not otp:
        print("❌ No OTP provided to send_email function")
        return None

    # 1. Message Setup
    msg = EmailMessage()
    msg.set_content(f"Hello,\n\nYour Digital Bank OTP is: {otp}\n\nThis code will expire in 5 minutes. Do not share it with anyone.")
    msg["Subject"] = "Digital Bank OTP"
    msg["From"] = GMAIL_USER
    msg["To"] = receiver_email

    # 2. Sending Logic (Port 587 + STARTTLS)
    try:
        # SMTP Server setup
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure connection start pannum
        
        # Login and Send
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ OTP sent successfully to {receiver_email} via Port 587!")
        return True
    except Exception as e:
        print(f"❌ SMTP 587 Error: {e}")
        return False
