import os
import base64
import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import argparse

# Set your SendGrid API key here
SENDGRID_API_KEY = "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"

parser = argparse.ArgumentParser()
parser.add_argument('--to_email', required=True)
parser.add_argument('--file_name', default="combined_enriched_output.csv")
parser.add_argument('--subject', default="CIAN Report")
parser.add_argument('--body', default="Please find attached the latest listings.")
args = parser.parse_args()

file_path = os.path.join("output/CSV", args.file_name)
is_excel = file_path.endswith(".xlsx")

def send_email_with_attachment(to_email, subject, body, file_path, is_excel):
    message = Mail(
        from_email="fedoseevafedoseeva@gmail.com",  # Replace with your verified SendGrid sender
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
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
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent to {to_email}! Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Run it
send_email_with_attachment(
    to_email=args.to_email,
    subject=args.subject,
    body=args.body,
    file_path=file_path,
    is_excel=is_excel
)
