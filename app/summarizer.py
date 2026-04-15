from transformers import pipeline

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_complaint(text):

    summary = summarizer(text,max_length=40,min_length=10)

    return summary[0]["summary_text"]
