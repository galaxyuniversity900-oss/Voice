from dataclasses import dataclass
from typing import Final

@dataclass(frozen=True)
class DialectProfile:
    id: str
    locale: str
    name_ar: str
    name_en: str
    region: str
    aliases: tuple[str, ...] = ()

ARABIC_DIALECTS: Final[dict[str, DialectProfile]] = {
    "ar-eg": DialectProfile("ar-eg", "ar-EG", "العربية المصرية", "Egyptian Arabic", "Egypt", ("egyptian", "masri", "مصري", "مصرية")),
    "ar-sa": DialectProfile("ar-sa", "ar-SA", "العربية السعودية", "Saudi Arabic", "Saudi Arabia"),
    "ar-ae": DialectProfile("ar-ae", "ar-AE", "العربية الإماراتية", "Emirati Arabic", "United Arab Emirates"),
    "ar-kw": DialectProfile("ar-kw", "ar-KW", "العربية الكويتية", "Kuwaiti Arabic", "Kuwait"),
    "ar-qa": DialectProfile("ar-qa", "ar-QA", "العربية القطرية", "Qatari Arabic", "Qatar"),
    "ar-bh": DialectProfile("ar-bh", "ar-BH", "العربية البحرينية", "Bahraini Arabic", "Bahrain"),
    "ar-om": DialectProfile("ar-om", "ar-OM", "العربية العُمانية", "Omani Arabic", "Oman"),
    "ar-gulf": DialectProfile("ar-gulf", "ar", "العربية الخليجية", "Gulf Arabic", "Gulf"),
    "ar-msa": DialectProfile("ar-msa", "ar", "العربية الفصحى", "Modern Standard Arabic", "Arabic"),
}

def get_dialect(dialect_id: str) -> DialectProfile:
    try:
        return ARABIC_DIALECTS[dialect_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported Arabic dialect: {dialect_id}") from exc
