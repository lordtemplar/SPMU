def split_or_single(text):
    text = str(text).strip()
    if "•" in text:
        return [item.strip("• ").strip() for item in text.split("•") if item.strip()]
    else:
        return [text] if text else []
