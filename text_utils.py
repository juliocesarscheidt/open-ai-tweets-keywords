import re

URL_REGEX = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"


def sanitize_text(text: str):
    if text is None:
        return None
    text = text.strip().lower()
    # replace everything that is not included in the following chars
    text = re.sub(r"[^\w\s!#$%&\(\)\*\+,-—\./:;<=>\?@[\]^_´`\{\}|~]+", "", text)
    text = re.sub(r"^#", "", text)
    text = re.sub(r"\t", " ", text)
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text
