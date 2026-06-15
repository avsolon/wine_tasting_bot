from aiogram import Dispatcher
from app.bot.handlers import (
    start,
    tastings,
    registration,
    wines,
    gallery,
    reviews,
    contacts,
    admin,
)

dp = Dispatcher()
dp.include_router(start.router)
dp.include_router(tastings.router)
dp.include_router(registration.router)
dp.include_router(wines.router)
dp.include_router(gallery.router)
dp.include_router(reviews.router)
dp.include_router(contacts.router)
dp.include_router(admin.router)
