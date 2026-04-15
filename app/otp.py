import secrets
from datetime import datetime, timedelta

otp_store = {}

def generate_otp(email):
    # Prevent spamming: Check if OTP was sent in the last 30 seconds
    if email in otp_store:
        if datetime.now() - otp_store[email]["time"] < timedelta(seconds=30):
            return None

    otp = str(secrets.randbelow(900000) + 100000)
    otp_store[email] = {"otp": otp, "time": datetime.now()}
    return otp

def verify_otp(email, user_otp):
    if email not in otp_store:
        return False, "OTP not found. Please request a new one."

    data = otp_store[email]

    # Check expiration (5 minutes)
    if datetime.now() - data["time"] > timedelta(minutes=5):
        del otp_store[email]
        return False, "OTP has expired."

    if data["otp"] == user_otp:
        del otp_store[email]
        return True, "OTP Verified successfully!"

    return False, "Incorrect OTP code."