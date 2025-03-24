import os
import base64
import datetime
import argparse
import pandas as pd
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition

# ==== Функция для генерации HTML-превью ====
def generate_preview_html(file_path, max_items=10):
    try:
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)

        # Преобразуем offer_date в datetime и сортируем по убыванию
        if 'offer_date' in df.columns:
            df['offer_date'] = pd.to_datetime(df['offer_date'], errors='coerce')
            df = df.sort_values(by='offer_date', ascending=False)

        df = df.head(max_items)
        html_blocks = []

        for i, row in enumerate(df.itertuples(), start=1):
            oblast = getattr(row, 'geo_oblast', '–')
            okrug = getattr(row, 'geo_okrug', '–')
            address = getattr(row, 'geo_address_user', '–')
            price = f"{int(getattr(row, 'price', 0)):,} ₽".replace(",", " ")
            payback = int(getattr(row, 'median_payback_months', 0)) if not pd.isna(getattr(row, 'median_payback_months', 0)) else "–"
            obj_id = getattr(row, 'id', '–')
            url = getattr(row, 'url', '#')
            jk = getattr(row, 'geo_jk', '')
            jkUrl = getattr(row, 'jkUrl', '')
            photos = getattr(row, 'photo_thumbnailUrls', '')
            image_url = photos.split(',')[0].strip() if isinstance(photos, str) and photos else None

            block = f"""
                <div style="display: flex; align-items: flex-start; border:1px solid #ccc; padding:10px; margin:10px 0; font-family:Arial, sans-serif;">
                    <div style="flex: 1; padding-right: 15px;">
                        <h3>{i}. {oblast}, {okrug}</h3>
                        <p><strong>📍 </strong> {address}</p>
                        <p><strong>Цена:</strong> {price}</p>
                        <p><strong>Окупаемость:</strong> {payback} мес.</p>
                        <p><a href="{url}" target="_blank">🔗 ID: {obj_id}</a></p>
                        <p><a href="{jkUrl}" target="_blank">🏢 ЖК: {jkUrl}</a></p>
            """

            block += "</div>"

            # 📷 Фото: берём до 3 ссылок
            image_urls = []
            if isinstance(photos, str):
                if ';' in photos:
                    image_urls = [p.strip() for p in photos.split(';') if p.strip()]
                else:
                    image_urls = [p.strip() for p in photos.split(',') if p.strip()]
                image_urls = image_urls[:3]  # только первые 3

            if image_urls:
                block += '<div style="margin-top:10px; text-align: center;">'
                for img in image_urls:
                    if img.startswith("http"):
                        block += f'''
                            <div style="margin-bottom: 6px;">
                                <img src="{img}" style="width:100%; max-width:150px; border-radius:4px; display:inline-block;">
                            </div>
                        '''
                block += '</div>'



            block += "</div>"
            html_blocks.append(block)

        return "<html><body><h2 style='font-family:Arial,sans-serif;'>🔥 Новые объекты CIAN</h2>" + "".join(html_blocks) + "</body></html>"

    except Exception as e:
        print(f"Error generating preview: {e}")
        return "<p>Не удалось создать превью объявлений</p>"



# ==== Аргументы ====
parser = argparse.ArgumentParser()
parser.add_argument('--to_email', required=True)
parser.add_argument('--file_name', default="combined_enriched_output.csv")
parser.add_argument('--subject', default="CIAN Report")
parser.add_argument('--body', default="Новые объявления прилагаются.")
args = parser.parse_args()

file_path = os.path.join("output/CSV", args.file_name)
is_excel = file_path.endswith(".xlsx")

# ==== Функция отправки ====
def send_email_with_attachment(to_email, subject, body, file_path, is_excel):
    html_content = generate_preview_html(file_path)

    message = Mail(
        from_email="fedoseevafedoseeva@gmail.com",
        to_emails=to_email,
        subject=subject,
        html_content=Content("text/html", html_content)
    )

    with open(file_path, "rb") as f:
        data = f.read()
        f_encoded = base64.b64encode(data).decode()

    date_suffix = datetime.datetime.now().strftime("%Y%m%d")
    ext = ".xlsx" if is_excel else ".csv"
    renamed_filename = f"new_listings_{date_suffix}{ext}"

    mime_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if is_excel else "text/csv"
    )

    attachment = Attachment(
        FileContent(f_encoded),
        FileName(renamed_filename),
        FileType(mime_type),
        Disposition("attachment")
    )

    message.attachment = attachment

    try:
        sg = SendGridAPIClient("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")
        response = sg.send(message)
        print(f"Email sent to {to_email}! Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

# ==== Запуск ====
send_email_with_attachment(
    to_email=args.to_email,
    subject=args.subject,
    body=args.body,
    file_path=file_path,
    is_excel=is_excel
)
