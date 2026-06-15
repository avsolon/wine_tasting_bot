from datetime import datetime, timedelta


def parse_date(date_str: str) -> datetime | None:
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def format_date(date_str: str) -> str:
    dt = parse_date(date_str)
    if dt:
        months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря",
        ]
        return f"{dt.day} {months[dt.month - 1]} {dt.year}"
    return date_str


def is_past(date_str: str) -> bool:
    dt = parse_date(date_str)
    if dt:
        return dt.date() < datetime.now().date()
    return False


def days_until(date_str: str) -> int:
    dt = parse_date(date_str)
    if dt:
        delta = dt.date() - datetime.now().date()
        return delta.days
    return 0


def get_reminder_date(date_str: str) -> datetime | None:
    dt = parse_date(date_str)
    if dt:
        return dt + timedelta(days=1)
    return None
