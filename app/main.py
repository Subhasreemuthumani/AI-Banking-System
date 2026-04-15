from fastapi import FastAPI, Request, Form, BackgroundTasks, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uuid
from fpdf import FPDF
from fastapi.responses import FileResponse


# Intha imports unga folder-la irukura files-oda match aaganum
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

# -------------------------
# HOME PAGE
# -------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------------
# REGISTRATION
# -------------------------
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

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

# -------------------------
# LOGIN & OTP
# -------------------------
@app.get("/")
def home(request: Request):
    # 'context' nu mention panna thaan pudhu version-la work aagum
    return templates.TemplateResponse(request=request, name="index.html")

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
        # Browser-la secure cookie set pandrom
        response.set_cookie(key="session_user", value=email, httponly=True)
        return {"message": "Login successful", "status": "success"}
    return {"error": msg}

# -------------------------
# DASHBOARD (Auto-fills Data)
# -------------------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user_email = request.cookies.get("session_user")
    if not user_email:
        return RedirectResponse(url="/login")

    user_data = users.find_one({"email": user_email})
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user_data})

# -------------------------
# MY COMPLAINTS (User History)
# -------------------------
@app.get("/my-complaints", response_class=HTMLResponse)
def my_complaints(request: Request):
    user_email = request.cookies.get("session_user")
    if not user_email:
        return RedirectResponse(url="/login")

    user_data = users.find_one({"email": user_email})
    # Filter complaints by the logged-in user's account number
    user_history = list(complaints.find({"account_number": user_data["account_number"]}))

    return templates.TemplateResponse("my_complaints.html", {
        "request": request,
        "complaints": user_history,
        "user": user_data
    })

# -------------------------
# AI PREDICTION
# -------------------------
from datetime import datetime
import smtplib
from email.message import EmailMessage
from datetime import datetime
import uuid

# --- 1. EMAIL SENDING LOGIC (Add this above your routes) ---
def send_confirmation_email(user_email, ticket_id, category, severity, res_time):
    try:
        msg = EmailMessage()
        msg['Subject'] = f"🏦 AI Bank: Complaint Registered - Ticket #{ticket_id}"
        msg['From'] = "digitalbank93@gmail.com"  # Replace with your email
        msg['To'] = user_email

        # Professional English Content
        content = f"""
Dear Customer,

Thank you for contacting AI Digital Bank. We have successfully registered your complaint.

TICKET DETAILS:
---------------------------------------------
Ticket ID          : {ticket_id}
Category           : {category}
Priority Level     : {severity}
Current Status     : PENDING
Expected Resolution: {res_time}
---------------------------------------------

AI ANALYSIS SUMMARY:
Our AI system has categorized your issue and routed it to the specialized department. 
You can track the progress and download your official PDF receipt on our portal.

Thank you for your patience.

Regards,
Customer Support Team
AI Digital Bank
        """
        msg.set_content(content)

        # SMTP Server Setup
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("digitalbank93@gmail.com", "naiflulwjhpxqoli") # Use App Password
            smtp.send_message(msg)
        print(f"✅ Email notification sent to {user_email}")
    except Exception as e:
        print(f"❌ Email failed: {e}")


# --- 2. UPDATED PREDICT ROUTE ---
@app.post("/predict")
def predict(
    text: str = Form(...),
    account_number: str = Form(...),
    customer_name: str = Form(...),
    email: str = Form(...) # New email field from frontend
):
    # 1. SPAM CHECK LOGIC
    spam_status = "Safe"
    last_entry = complaints.find_one({"account_number": account_number}, sort=[("time", -1)])
    if last_entry and last_entry['text'] == text:
        spam_status = "Potential Spam (Duplicate Text)"

    # 2. AI ANALYSIS (Classification, Summarization, Fraud)
    result = predict_complaint(text)
    summary = summarize_complaint(text)
    fraud = fraud_risk(text)
    ticket_id = str(uuid.uuid4())[:8]
    
    # Root Cause & Dept Extraction
    root_cause_val = result.get("root_cause", "General Issue")
    dept_val = result.get("department", "Customer Support")
    severity_val = result.get("severity", "Low")

    # 3. ADVANCED FEATURE: RESOLUTION TIME PREDICTION
    res_time = "3-5 Working Days"
    if severity_val == "High":
        res_time = "Within 24 Hours (Priority)"
    elif severity_val == "Medium":
        res_time = "48-72 Hours"

    # 4. INSERT INTO DATABASE
    complaint_data = {
        "ticket_id": ticket_id,
        "account_number": account_number,
        "customer_name": customer_name,
        "email": email, # Saving email
        "text": text,
        "summary": summary,
        "category": result["category"],
        "severity": severity_val,
        "department": dept_val,
        "root_cause": root_cause_val,
        "expected_resolution": res_time, # Prediction stored
        "fraud_risk": fraud,
        "spam_check": spam_status,
        "status": "Pending",
        "time": current_time()
    }
    complaints.insert_one(complaint_data)

    # 5. TRIGGER EMAIL NOTIFICATION
    # IMPORTANT: Ensure your internet is connected
    send_confirmation_email(email, ticket_id, result["category"], severity_val, res_time)

    # 6. RETURN RESPONSE TO FRONTEND
    return {
        "ticket_id": ticket_id,
        "summary": summary,
        "category": result["category"],
        "severity": severity_val,
        "department": dept_val,
        "root_cause": root_cause_val,
        "expected_resolution": res_time,
        "fraud_risk": fraud,
        "spam_check": spam_status,
        "status": "Pending"
    }
# -------------------------
# LOGOUT
# -------------------------
@app.get("/logout")
def logout(response: Response):
    # Cookie-ah delete panni Redirect pandrom
    response = RedirectResponse(url="/login")
    response.delete_cookie("session_user")
    return response

# -------------------------
# ADMIN VIEW
#
@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    # 1. Priority Order Define Pandrom (High Priority mela vara)
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    
    # 2. Database-la irundhu ella complaints-um edukkuron
    all_data = list(complaints.find())
    
    # 3. ADVANCED SORTING: 
    # Modhalla 'Pending' tickets varum, adhukulla 'High Severity' tickets mela varum.
    sorted_data = sorted(
        all_data, 
        key=lambda x: (
            x.get("status") != "Pending", # Pending tickets-ku priority
            priority_order.get(x.get("severity", "Low"), 3) # High Severity-ku priority
        )
    )

    # 4. DEPARTMENT-WISE SPLITTING (Counts for each dept)
    dept_stats = {
        "Customer Support": complaints.count_documents({"department": "Customer Support"}),
        "IT/Technical": complaints.count_documents({"department": "IT/Technical"}),
        "Fraud/Security": complaints.count_documents({"department": "Fraud/Security"}),
        "Loan/Finance": complaints.count_documents({"department": "Loan/Finance"})
    }

    # 5. OVERALL STATS
    stats = {
        "total": len(all_data),
        "pending": complaints.count_documents({"status": "Pending"}),
        "resolved": complaints.count_documents({"status": "Resolved"}),
        "spam": complaints.count_documents({"status": "Rejected/Spam"}),
        "depts": dept_stats # Intha data UI-la cards-aa varum
    }

    return templates.TemplateResponse(
        "admin.html", 
        {
            "request": request, 
            "data": sorted_data, 
            "stats": stats
        }
    )
@app.post("/update-status")
def update_status(background_tasks: BackgroundTasks, ticket_id: str = Form(...), status: str = Form(...)):
    # 1. Database-la status update pandrom
    complaints.update_one({"ticket_id": ticket_id}, {"$set": {"status": status}})
    
    # 2. User email-ah fetch pandrom
    complaint_data = complaints.find_one({"ticket_id": ticket_id})
    user_data = users.find_one({"account_number": complaint_data["account_number"]})
    user_email = user_data["email"]

    # 3. Custom message ready pandrom
    subject = f"Update on your Complaint Ticket #{ticket_id}"
    message = f"""
    Hello {user_data['username']},

    The status of your complaint regarding '{complaint_data['category']}' has been updated to: {status}.
    
    Ticket ID: {ticket_id}
    Thank you for banking with AI BANK.
    """

    # 4. Background task-la email anupuroam
    background_tasks.add_task(send_email, user_email, message) # Email logic-ah use pandrom

    return {"message": f"Status updated to {status} and notification sent to user."}
# -------------------------
# TEMPORARY: CLEAR DATABASE
# -------------------------
@app.get("/clear-my-data")
def clear_data():
    complaints.delete_many({}) # This deletes ALL complaints
    return {"message": "Database cleaned successfully! You can now delete this route."}

import os # Header-la idhu kandaipa irukanum

@app.get("/download-ticket/{ticket_id}")
def download_ticket(ticket_id: str):
    complaint = complaints.find_one({"ticket_id": ticket_id})
    if not complaint:
        return {"error": "Ticket not found"}

    # FOLDER CHECK & CREATE (Intha 2 lines thaan missing)
    if not os.path.exists("tickets"):
        os.makedirs("tickets")

    pdf = FPDF()
    pdf.add_page()
    
    # Safe text conversion (Encoding issues varaama irukka)
    def s(text): return str(text).encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="AI DIGITAL BANK - COMPLAINT RECEIPT", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Ticket ID: {s(complaint['ticket_id'])}", ln=True)
    pdf.cell(200, 10, txt=f"Customer Name: {s(complaint['customer_name'])}", ln=True)
    pdf.cell(200, 10, txt=f"Account Number: {s(complaint['account_number'])}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="AI Analysis Report:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Category: {s(complaint['category'])}", ln=True)
    pdf.cell(200, 10, txt=f"Severity: {s(complaint['severity'])}", ln=True)
    pdf.cell(200, 10, txt=f"Root Cause: {s(complaint['root_cause'])}", ln=True)
    pdf.ln(5)
    
    pdf.multi_cell(0, 10, txt=f"Description: {s(complaint['text'])}")
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Current Status: {s(complaint['status'])}", ln=True)

    file_path = f"tickets/ticket_{ticket_id}.pdf"
    pdf.output(file_path)
    
    return FileResponse(file_path, filename=f"Ticket_{ticket_id}.pdf")


# --- EMAIL NOTIFICATION LOGIC ---
@app.post("/resolve-complaint")

def resolve_complaint(ticket_id: str = Form(...), resolution_note: str = Form(...)):

    # 1. Update MongoDB with Status and Note

    result = complaints.update_one(

        {"ticket_id": ticket_id},

        {"$set": {

            "status": "Resolved",

            "resolution_note": resolution_note,

            "resolved_at": datetime.now()

        }}

    )



    if result.modified_count > 0:

        # 2. Get User Email to send notification

        complaint = complaints.find_one({"ticket_id": ticket_id})

        user_email = complaint.get('email')

       

        # 3. Trigger Professional English Email

        if user_email:

            send_resolution_email(user_email, ticket_id, resolution_note)

           

        return {"message": "Complaint Resolved and Customer Notified!"}

    return {"error": "Ticket not found"}



# Email function update (English-la professional-aa irukkum)

def send_resolution_email(to_email, ticket_id, note):

    try:

        msg = EmailMessage()

        msg['Subject'] = f"✅ Resolved: Your Complaint #{ticket_id}"

        msg['From'] = "your-bank-email@gmail.com"

        msg['To'] = to_email

        msg.set_content(f"""

Dear Customer,



We are pleased to inform you that your complaint (Ticket #{ticket_id}) has been resolved.



OFFICIAL RESOLUTION NOTE:

---------------------------------------------

{note}

---------------------------------------------



Our team has taken the necessary actions based on the AI analysis and internal review.

You can now download the updated final receipt from your dashboard.



Thank you for banking with us!



Regards,

Customer Support Team

AI Digital Bank

        """)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:

            smtp.login("your-bank-email@gmail.com", "your-app-password")

            smtp.send_message(msg)

    except Exception as e:

        print(f"Mail Error: {e}")

