from app.core.config import settings


def is_admin(telegram_id: int) -> bool:
    return telegram_id in settings.admin_ids_list
