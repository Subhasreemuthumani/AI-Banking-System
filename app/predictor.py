import joblib

# Load models
vectorizer = joblib.load("models/vectorizer.pkl")

category_model = joblib.load("models/category_model.pkl")

severity_model = joblib.load("models/severity_model.pkl")

root_model = joblib.load("models/rootcause_model.pkl")


def route_department(category):

    if category == "Credit card":
        return "Credit Card Department"

    elif category == "Mortgage":
        return "Loan Department"

    elif category == "Bank account":
        return "Retail Banking"

    elif category == "Money transfer":
        return "Payments Department"

    else:
        return "Customer Support"


def predict_complaint(text):

    # Convert text to vector
    X = vectorizer.transform([text])

    # Predict values
    category = category_model.predict(X)[0]

    severity = severity_model.predict(X)[0]

    root = root_model.predict(X)[0]

    department = route_department(category)

    return {

        "category": category,
        "severity": severity,
        "root_cause": root,
        "department": department

    }