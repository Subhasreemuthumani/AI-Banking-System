# ---------------------------------
# IMPORT LIBRARIES
# ---------------------------------
import pandas as pd
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# ---------------------------------
# DATA LOADING
# ---------------------------------
print("Loading dataset...")

data = pd.read_csv("data/complaints.csv")


# ---------------------------------
# DATA CLEANING
# ---------------------------------
# Remove rows where complaint text is missing
data = data.dropna(subset=["Consumer complaint narrative"])

print("Total complaints after cleaning:", len(data))


# ---------------------------------
# DATA SAMPLING (REDUCE DATA SIZE)
# ---------------------------------
# Large datasets slow down training
# So we take a sample of 20,000 complaints

data = data.sample(n=20000, random_state=42)

print("Sampled dataset size:", len(data))


# ---------------------------------
# FEATURE SELECTION
# ---------------------------------
# Extract required columns

data["text"] = data["Consumer complaint narrative"]
data["category"] = data["Product"]
data["root"] = data["Issue"]


# ---------------------------------
# SEVERITY LABEL CREATION
# ---------------------------------
# Create severity levels based on issue keywords

def detect_severity(issue):

    issue = str(issue).lower()

    if "fraud" in issue or "unauthorized" in issue:
        return "High"

    elif "delay" in issue or "pending" in issue:
        return "Medium"

    else:
        return "Low"


data["severity"] = data["root"].apply(detect_severity)


# ---------------------------------
# TEXT VECTORIZATION
# ---------------------------------
print("Converting text to numerical features...")

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=5000
)

X = vectorizer.fit_transform(data["text"])


# ---------------------------------
# MODEL TRAINING
# ---------------------------------
print("Training AI models...")

# Category Prediction Model
category_model = LogisticRegression(max_iter=200)
category_model.fit(X, data["category"])

# Severity Prediction Model
severity_model = LogisticRegression(max_iter=200)
severity_model.fit(X, data["severity"])

# Root Cause Prediction Model
root_model = LogisticRegression(max_iter=200)
root_model.fit(X, data["root"])


# ---------------------------------
# MODEL SAVING
# ---------------------------------
print("Saving trained models...")

pickle.dump(vectorizer, open("models/vectorizer.pkl", "wb"))

pickle.dump(category_model, open("models/category_model.pkl", "wb"))

pickle.dump(severity_model, open("models/severity_model.pkl", "wb"))

pickle.dump(root_model, open("models/rootcause_model.pkl", "wb"))


# ---------------------------------
# TRAINING COMPLETE
# ---------------------------------
print("AI Model Training Completed Successfully!")