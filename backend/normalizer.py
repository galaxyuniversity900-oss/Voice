import re

_ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")


def normalize_arabic(text: str) -> str:
    """Conservative normalization; preserves dialect wording rather than translating it."""
    text = text.replace("ـ", "")
    text = _ARABIC_DIACRITICS.sub("", text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def prepare_text(text: str, dialect: str) -> str:
    if dialect != "ar-eg":
        return normalize_arabic(text)
    # Egyptian profile is intentionally conservative: dialect words stay untouched.
    # Pronunciation lexicons/adapters can be added without changing the public API.
    return normalize_arabic(text)
