import requests
import pandas as pd
from datetime import datetime

TELEGRAM_TOKEN = '8474295044:AAF8vIpC-d9jcaPytpszmFQuVY9jHJza8Oc'
CHAT_ID = '-5007976823'


def send_message(text, parse_mode="HTML"):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': True
    }
    requests.post(url, data=payload)


def send_listings_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    if df.empty:
        return

    today = datetime.today().strftime('%d.%m.%Y')
    send_message(f"CIAN — {len(df)} новых объектов — {today}")

    for _, row in df.iterrows():
        bitrix_id = row.get("bitrix_id")
        bitrix_url = f"https://doverent.bitrix24.ru/crm/type/1032/details/{bitrix_id}/" if pd.notna(bitrix_id) else None

        text = f"""
🏢 <b>{row.get('geo_okrug', 'Объект')}</b>
📍 {row.get('geo_address_user', 'Адрес не указан')}
📐 {row.get('totalArea', '?')} м² | 🏗️ {row.get('buildYear', '—')} | 🏢 {row.get('floorsCount', '—')} эт.
💰 {int(row.get('price', 0)):,} ₽ | {int(row.get('price_per_meter', 0)):,} ₽/м²
📊 Окупаемость: {row.get('median_payback_months', '—')} мес.
🔗 <a href='{row.get('url', '#')}'>Объявление CIAN</a>"""

        if bitrix_url:
            text += f"\n🗂️ <a href='{bitrix_url}'>CRM карточка</a>"

        send_message(text)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_path', required=True, help='Path to CSV file with listings')
    args = parser.parse_args()
    send_listings_from_csv(args.csv_path)
