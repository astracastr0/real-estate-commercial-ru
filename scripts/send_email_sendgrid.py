import os
import base64
import datetime  # Add this import statement
import time  # Import the time module
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

# Set your SendGrid API key here
SENDGRID_API_KEY = "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"
current_date = datetime.datetime.now().strftime("%y%m%d")

def send_email_with_attachment(to_email, subject, body, file_path):
    message = Mail(
        from_email="fedoseevafedoseeva@gmail.com",  # Replace with your verified SendGrid email
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )

    # Attach the file
    with open(file_path, "rb") as f:
        file_data = f.read()
        encoded_file = base64.b64encode(file_data).decode()

    attachment = Attachment(
        FileContent(encoded_file),
        FileName(os.path.basename(file_path)),
        FileType("application/octet-stream"),
        Disposition("attachment"),
    )

    message.attachment = attachment

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent! Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Usage example
send_email_with_attachment(
    to_email="fedora121@gmail.com",  # Replace with the recipient's email
    subject="Here is your file",
    body="Please find the attached file.",
    file_path = os.path.join('output/CSV/', f'combined_enriched_output_{current_date}.csv')  # Change to your file path
)
