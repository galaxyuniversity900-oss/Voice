from __future__ import annotations

import re

from .dialects import get_dialect
from .normalizer import prepare_text

_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def preprocess(text: str, language: str, dialect: str) -> dict[str, str]:
    profile = get_dialect(dialect)
    cleaned = prepare_text(text, dialect)
    cleaned = cleaned.translate(_ARABIC_DIGITS)
    cleaned = re.sub(r"\s+([،؛,.!?؟])", r"\1", cleaned)
    return {
        "language": language,
        "dialect": profile.locale,
        "dialect_id": profile.id,
        "text": cleaned,
    }
