from app.database.models.tasting import Tasting
from app.database.models.wine import Wine
from app.database.models.application import Application
from app.database.models.review import Review
from app.utils.datetime_helper import format_date


def format_tasting(tasting: Tasting) -> str:
    return (
        f"🍷 *{tasting.title}*\n\n"
        f"📅 *Дата:* {format_date(tasting.date)}\n"
        f"⏰ *Время:* {tasting.time}\n"
        f"💰 *Стоимость:* {tasting.price} ₽\n"
        f"🎫 *Свободно мест:* {tasting.available_seats} / {tasting.total_seats}\n\n"
        f"📖 *Описание:*\n{tasting.description or 'Нет описания'}"
    )


def format_wine(wine: Wine) -> str:
    parts = [f"🍷 *{wine.name}*"]
    if wine.country:
        parts.append(f"🌍 *Страна:* {wine.country}")
    if wine.region:
        parts.append(f"📍 *Регион:* {wine.region}")
    if wine.grape:
        parts.append(f"🍇 *Сорт:* {wine.grape}")
    if wine.description:
        parts.append(f"\n📖 *Описание:*\n{wine.description}")
    return "\n".join(parts)


def format_application(application: Application, tasting_title: str) -> str:
    return (
        f"🍷 *Новая заявка*\n\n"
        f"*Мероприятие:* {tasting_title}\n"
        f"*Имя:* {application.name}\n"
        f"*Телефон:* {application.phone}\n"
        f"*Гостей:* {application.guests_count}\n"
        f"*Комментарий:* {application.comment or '—'}"
    )


def format_review(review: Review) -> str:
    text = f"⭐ *{review.author_name}*\n\n{review.text}"
    if review.rating:
        stars = "⭐" * review.rating
        text = f"{stars}\n\n{text}"
    if review.source_url:
        text += f"\n\n[Источник]({review.source_url})"
    return text


def format_application_card(application: Application, tasting_title: str) -> str:
    return (
        f"📋 *Заявка #{application.id}*\n\n"
        f"*Мероприятие:* {tasting_title}\n"
        f"*Имя:* {application.name}\n"
        f"*Телефон:* {application.phone}\n"
        f"*Гостей:* {application.guests_count}\n"
        f"*Комментарий:* {application.comment or '—'}\n"
        f"*Статус:* {application.status}\n"
        f"*CRM Lead ID:* {application.crm_lead_id or '—'}\n"
        f"*Дата:* {application.created_at}"
    )


def format_statistics(
    total_tastings: int,
    total_applications: int,
    total_guests: int,
    avg_fill: float,
    next_event: str | None,
) -> str:
    return (
        "📊 *Статистика*\n\n"
        f"📅 Всего дегустаций: *{total_tastings}*\n"
        f"📝 Всего заявок: *{total_applications}*\n"
        f"👥 Всего участников: *{total_guests}*\n"
        f"📈 Средняя заполняемость: *{avg_fill:.1f}%*\n"
        f"🍷 Ближайшее мероприятие: *{next_event or '—' }*"
    )
