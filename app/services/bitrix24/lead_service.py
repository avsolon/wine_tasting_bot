import aiohttp
from loguru import logger
from app.core.config import settings


class Bitrix24LeadService:
    def __init__(self):
        self.webhook_url = settings.BITRIX24_WEBHOOK_URL

    async def create_lead(
        self,
        name: str,
        phone: str,
        comment: str | None = None,
        event_name: str | None = None,
        telegram_id: int | None = None,
        price: float | None = None,
        guests_count: int = 1,
    ) -> str | None:
        if not self.webhook_url:
            logger.warning("Bitrix24 webhook URL not configured, skipping lead creation")
            return None

        total = price * guests_count if price else 0

        fields = {
            "TITLE": f"Запись на дегустацию: {event_name or ''}",
            "NAME": name,
            "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}],
            "COMMENTS": comment or "",
            "OPPORTUNITY": total,
            "CURRENCY_ID": "RUB",
        }
        if event_name:
            fields["UF_EVENT_NAME"] = event_name
        if telegram_id:
            fields["UF_TELEGRAM_ID"] = str(telegram_id)

        url = f"{self.webhook_url}/crm.lead.add.json"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={"fields": fields, "params": {"REGISTER_SONET_EVENT": "Y"}}) as resp:
                    data = await resp.json()
                    if "result" in data:
                        lead_id = str(data["result"])
                        logger.info(f"Bitrix24 lead created: {lead_id}")
                        return lead_id
                    else:
                        logger.error(f"Bitrix24 error: {data}")
                        return None
        except Exception as e:
            logger.error(f"Bitrix24 request failed: {e}")
            return None
