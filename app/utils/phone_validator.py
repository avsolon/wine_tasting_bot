import re
from app.core.constants import PHONE_REGEX


def validate_phone(phone: str) -> bool:
    return bool(re.match(PHONE_REGEX, phone.strip()))


def format_phone(phone: str) -> str:
    cleaned = re.sub(r"[^\d]", "", phone)
    if cleaned.startswith("8"):
        cleaned = "7" + cleaned[1:]
    if len(cleaned) == 11:
        return f"+{cleaned[0]} ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:9]}-{cleaned[9:11]}"
    return phone
