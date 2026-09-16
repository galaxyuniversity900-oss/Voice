import re

_ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")


def normalize_arabic(text: str, preserve_diacritics: bool = False) -> str:
    """Conservative Arabic normalization with optional vowel-mark preservation."""
    text = text.replace("ـ", "")
    if not preserve_diacritics:
        text = _ARABIC_DIACRITICS.sub("", text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def prepare_text(text: str, dialect: str) -> str:
    # KemeTone uses Arabic vowel marks to improve Egyptian pronunciation.
    return normalize_arabic(text, preserve_diacritics=dialect == "ar-eg")
