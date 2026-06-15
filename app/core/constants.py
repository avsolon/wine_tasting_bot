WELCOME_MESSAGE = (
    "Добро пожаловать в клуб винных дегустаций «Tasting & Talk»! 🍷\n\n"
    "Здесь вы можете записаться на ближайшие мероприятия, "
    "узнать о вине и атмосфере клуба. Добро пожаловать!"
)

REGISTRATION_CONFIRMATION = (
    "✅ Благодарим за запись!\n\n"
    "Мы получили вашу заявку и вскоре наш менеджер свяжется с вами."
)

TastingStatus = type("TastingStatus", (), {"ACTIVE": "active", "FINISHED": "finished"})
ApplicationStatus = type(
    "ApplicationStatus", (), {"PENDING": "pending", "CONFIRMED": "confirmed", "CANCELLED": "cancelled"}
)

REVIEW_REMINDER_DELAY_DAYS = 1

PHONE_REGEX = r"^(\+7|8)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$"

# Уведомление после записи: текст поверх базового REGISTRATION_CONFIRMATION
REGISTRATION_CONFIRMATION_EXTRA = "🍷 *Детали мероприятия:*\n{details}"

REMINDER_24H_TEXT = (
    "🔔 *Напоминание*\n\n"
    "Завтра состоится дегустация, на которую вы записаны! 🍷\n\n"
    "Ждём вас!"
)

REMINDER_1H_TEXT = (
    "🔔 *Напоминание*\n\n"
    "Дегустация начнётся через 1 час! 🍷\n\n"
    "Не опаздывайте!"
)

MAIN_MENU_BUTTONS = {
    "tastings": "🍷 Предстоящие дегустации",
    "register": "📝 Записаться",
    "wines": "🍇 Коллекция вин",
    "gallery": "📸 Фото и отзывы",
    "reviews": "⭐ Оставить отзыв",
    "contacts": "📍 Контакты",
}

ADMIN_MENU_BUTTONS = {
    "manage_tastings": "📅 Дегустации",
    "manage_wines": "🍷 Вина",
    "manage_gallery": "📸 Галерея",
    "manage_reviews": "⭐ Отзывы",
    "manage_applications": "📋 Заявки",
    "statistics": "📊 Статистика",
    "settings": "⚙️ Настройки",
}
