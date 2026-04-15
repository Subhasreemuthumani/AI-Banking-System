console.log("✅ Bank Script Loaded Successfully!");

// -------------------------
// 1. REGISTRATION LOGIC
// -------------------------
function registerUser() {
    let name = document.getElementById("reg_name").value;
    let email = document.getElementById("reg_email").value;
    let acc = document.getElementById("reg_acc").value;
    let ifsc = document.getElementById("reg_ifsc").value;
    let phone = document.getElementById("reg_phone").value;
    let pass = document.getElementById("reg_pass").value;

    // Ellaa fields-um fill aagi irukkanu check pannum
    if(!name || !email || !acc || !ifsc || !phone || !pass) {
        alert("Please fill all fields!");
        return;
    }

    let formData = new URLSearchParams();
    // Intha names unga main.py-la irukura parameters-oda match aaganum
    formData.append('name', name);
    formData.append('email', email);
    formData.append('acc', acc);
    formData.append('ifsc', ifsc);
    formData.append('phone', phone);
    formData.append('password', pass);

    fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString()
    })
    .then(res => res.json())
    .then(data => {
        if(data.error) {
            alert("Error: " + data.error);
        } else {
            alert(data.message); // Success message varum
            window.location.href = "/login";
        }
    })
    .catch(err => {
        console.error("Register Error:", err);
        alert("Connection Error! Check if server is running.");
    });
}
// -------------------------
// 2. LOGIN & OTP LOGIC
// -------------------------
function sendOTP() {
    let email = document.getElementById("email").value;
    if(!email) { alert("Please enter email"); return; }

    let formData = new URLSearchParams();
    formData.append('email', email);

    fetch("/send-otp", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString()
    })
    .then(res => res.json())
    .then(data => {
        if(data.error) alert(data.error);
        else alert(data.message);
    });
}

function verifyOTP() {
    let email = document.getElementById("email").value;
    let otp = document.getElementById("otp").value;

    let formData = new URLSearchParams();
    formData.append('email', email);
    formData.append('otp', otp);

    fetch("/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString()
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === "success") {
            alert("Login Success!");
            window.location = "/dashboard";
        } else {
            alert(data.error);
        }
    });
}

// -------------------------
// 3. AI COMPLAINT PREDICTION
function predict() {
    let text = document.getElementById("complaint").value;
    let name = document.getElementById("name").value;
    let account = document.getElementById("account").value;
    let btn = document.querySelector("button[onclick='predict()']"); // Button-ah select pandrom

    if (!text) { alert("Please describe your issue"); return; }

    // 1. Button-ah disable panni text-ah mathurom
    btn.disabled = true;
    btn.innerText = "Processing AI Analysis...";

    let formData = new URLSearchParams();
    formData.append('text', text);
    formData.append('customer_name', name);
    formData.append('account_number', account);

    fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString()
    })
    .then(res => res.json())
    .then(data => {
        // 2. Response vanthathum button-ah thirumba enable pandrom
        btn.disabled = false;
        btn.innerText = "🚀 Analyze & Submit Complaint";

        document.getElementById("result_card").style.display = "block";
        document.getElementById("category").innerText = data.category;
        document.getElementById("dept").innerText = data.department;
        document.getElementById("fraud").innerText = data.fraud_risk;
        document.getElementById("summary").innerText = data.summary;
        document.getElementById("ticket_id_display").innerText = data.ticket_id;
        document.getElementById("root_cause_display").innerText = data.root_cause;
        document.getElementById("download_section").style.display = "block";
        document.getElementById("pdf_download_link").href = "/download-ticket/" + data.ticket_id;


        let sev = document.getElementById("severity");
        sev.innerText = data.severity;
        if(data.severity === "High") sev.className = "badge bg-danger result-badge";
        else if(data.severity === "Medium") sev.className = "badge bg-warning text-dark result-badge";
        else sev.className = "badge bg-success result-badge";

        alert("Complaint Submitted Successfully!");
    })
    .catch(err => {
        btn.disabled = false;
        btn.innerText = "🚀 Analyze & Submit Complaint";
        alert("Error: " + err);
    });
}