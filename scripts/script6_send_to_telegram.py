import requests
from datetime import datetime

def send_to_telegram_from_df(df, bitrix_ids: dict, telegram_token: str, chat_id: str):
    def send_message(text, parse_mode="HTML"):
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }
        requests.post(url, data=payload)

    if df.empty:
        return

    today = datetime.today().strftime('%d.%m.%Y')
    send_message(f"📢 <b>CIAN — {len(df)} новых объектов — {today}</b>")

    for _, row in df.iterrows():
        row_id = str(row.get("id"))
        bitrix_id = bitrix_ids.get(row_id)
        if not bitrix_id:
            continue  # skip if no Bitrix ID

        cian_url = row.get("url", "#")
        bitrix_url = f"https://doverent.bitrix24.ru/crm/type/1032/details/{bitrix_id}/"

        # Fields
        area = row.get("totalArea", "—")
        build_year = row.get("buildYear", "—")
        floors = row.get("floorsCount", "—")
        price = row.get("price", 0)
        price_per_m = row.get("price_per_meter", 0)
        payback = row.get("median_payback_months", "—")
        address = row.get("geo_address_user", "Адрес не указан")
        okrug = row.get("geo_okrug", "Объект")

        # Format numbers
        if isinstance(price, (int, float)):
            price = f"{int(price):,}".replace(",", " ")
        if isinstance(price_per_m, (int, float)):
            price_per_m = f"{int(price_per_m):,}".replace(",", " ")

        # Compose message
        text = f"""
🏢 <b>{okrug}</b>
📍 {address}
📐 {area} м² | 🏗️ {build_year} | 🏢 {floors} эт.
💰 {price} ₽ | {price_per_m} ₽/м²
📊 Окупаемость: {payback} мес.

🔗 <a href="{cian_url}">Ссылка на CIAN</a>
🔗 <a href="{bitrix_url}">Открыть в Bitrix</a>
""".strip()

        send_message(text)
