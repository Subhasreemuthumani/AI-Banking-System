def fraud_risk(text):

    text=text.lower()

    if "unauthorized" in text:
        return "High Risk"

    if "fraud" in text:
        return "High Risk"

    if "scam" in text:
        return "High Risk"

    if "unknown transaction" in text:
        return "Medium Risk"

    return "Low Risk"