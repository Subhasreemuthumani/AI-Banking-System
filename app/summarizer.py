


def summarize_complaint(text):
    try:
        # AI model perusu-nu Render crash pannaama irukka 
        # Intha logic use pannuvom.
        if len(text) > 100:
            return text[:100] + "..."
        return text
    except Exception as e:
        return text
