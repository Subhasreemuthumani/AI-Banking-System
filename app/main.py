from fastapi import FastAPI, Request, Form, BackgroundTasks, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uuid
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from fpdf import FPDF
from fastapi.responses import FileResponse

# Internal Imports
from app.database import users, complaints
from app.auth import hash_password, verify_password
from app.predictor import predict_complaint
from app.summarizer import summarize_complaint
from app.fraud_detector import fraud_risk
from app.utils import current_time
from app.otp import generate_otp, verify_otp
from app.email import send_email

app = FastAPI()

# -------------------------
# STATIC & TEMPLATES
# -------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

print("✅ AI Digital Bank Backend - Full System Loaded")

# --- EMAIL LOGIC ---
def send_confirmation_email(user_email, ticket_id, category, severity, res_time):
    try:
        msg = EmailMessage()
        msg['Subject'] = f"🏦 AI Bank: Complaint Registered - Ticket #{ticket_id}"
        msg['From'] = "digitalbank93@gmail.com"
        msg['To'] = user_email
        content = f"""
Dear Customer,
Thank you for contacting AI Digital Bank. Ticket ID: {ticket_id}.
Category: {category} | Priority: {severity}
Expected Resolution: {res_time}
Regards, Support Team.
        """
        msg.set_content(content)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("digitalbank93@gmail.com", "naiflulwjhpxqoli")
            smtp.send_message(msg)
    except Exception as e:
        print(f"❌ Email failed: {e}")

# -------------------------
# ROUTES (TemplateResponse Fixed)
# -------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.post("/register")
def register(
    name: str = Form(...), 
    email: str = Form(...), 
    acc: str = Form(...), 
    ifsc: str = Form(...), 
    phone: str = Form(...), 
    password: str = Form(...)
):
    if users.find_one({"email": email}):
        return {"error": "Email already registered!"}
    cust_id = "BNK" + str(uuid.uuid4().int)[:6] 
    users.insert_one({
        "cust_id": cust_id,
        "username": name,
        "email": email,
        "account_number": acc,
        "ifsc": ifsc,
        "phone": phone,
        "password": hash_password(password)
    })
    return {"message": f"Success! Customer ID: {cust_id}"}

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/send-otp")
def send_otp_route(background_tasks: BackgroundTasks, email: str = Form(...)):
    user = users.find_one({"email": email})
    if not user:
        return {"error": "Email not registered!"}
    otp = generate_otp(email)
    if not otp:
        return {"error": "Please wait 30 seconds."}
    background_tasks.add_task(send_email, email, otp)
    return {"message": "OTP sent to your registered Gmail"}

@app.post("/verify-otp")
def verify(response: Response, email: str = Form(...), otp: str = Form(...)):
    success, msg = verify_otp(email, otp)
    if success:
        response.set_cookie(key="session_user", value=email, httponly=True)
        return {"message": "Login successful", "status": "success"}
    return {"error": msg}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user_email = request.cookies.get("session_user")
    if not user_email:
        return RedirectResponse(url="/login")
    user_data = users.find_one({"email": user_email})
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"user": user_data})

@app.get("/my-complaints", response_class=HTMLResponse)
def my_complaints(request: Request):
    user_email = request.cookies.get("session_user")
    if not user_email:
        return RedirectResponse(url="/login")
    user_data = users.find_one({"email": user_email})
    user_history = list(complaints.find({"account_number": user_data["account_number"]}))
    return templates.TemplateResponse(request=request, name="my_complaints.html", context={"complaints": user_history, "user": user_data})

@app.post("/predict")
def predict(
    text: str = Form(...),
    account_number: str = Form(...),
    customer_name: str = Form(...),
    email: str = Form(...)
):
    spam_status = "Safe"
    last_entry = complaints.find_one({"account_number": account_number}, sort=[("time", -1)])
    if last_entry and last_entry['text'] == text:
        spam_status = "Potential Spam (Duplicate)"

    result = predict_complaint(text)
    summary = summarize_complaint(text)
    fraud = fraud_risk(text)
    ticket_id = str(uuid.uuid4())[:8]
    
    severity_val = result.get("severity", "Low")
    res_time = "3-5 Working Days"
    if severity_val == "High": res_time = "Within 24 Hours"

    complaint_data = {
        "ticket_id": ticket_id, "account_number": account_number, "customer_name": customer_name,
        "email": email, "text": text, "summary": summary, "category": result["category"],
        "severity": severity_val, "department": result.get("department", "Support"),
        "root_cause": result.get("root_cause", "General"), "expected_resolution": res_time,
        "fraud_risk": fraud, "spam_check": spam_status, "status": "Pending", "time": current_time()
    }
    complaints.insert_one(complaint_data)
    send_confirmation_email(email, ticket_id, result["category"], severity_val, res_time)

    return {"ticket_id": ticket_id, "status": "Pending", "category": result["category"]}

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    all_data = list(complaints.find())
    stats = {
        "total": len(all_data),
        "pending": complaints.count_documents({"status": "Pending"}),
        "resolved": complaints.count_documents({"status": "Resolved"}),
        "depts": {"Support": 5} # Simple stats
    }
    return templates.TemplateResponse(request=request, name="admin.html", context={"data": all_data, "stats": stats})

@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/login")
    response.delete_cookie("session_user")
    return response

@app.get("/download-ticket/{ticket_id}")
def download_ticket(ticket_id: str):
    complaint = complaints.find_one({"ticket_id": ticket_id})
    if not os.path.exists("tickets"): os.makedirs("tickets")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="AI DIGITAL BANK RECEIPT", ln=True, align='C')
    file_path = f"tickets/ticket_{ticket_id}.pdf"
    pdf.output(file_path)
    return FileResponse(file_path, filename=f"Ticket_{ticket_id}.pdf")
