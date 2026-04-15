from transformers import pipeline

summarizer = pipeline("summarization")

def summarize_complaint(text):

    summary = summarizer(text,max_length=40,min_length=10)

    return summary[0]["summary_text"]