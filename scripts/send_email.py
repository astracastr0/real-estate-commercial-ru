import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

# Set your SendGrid API key here
SENDGRID_API_KEY = "YOUR_SENDGRID_API_KEY"

def send_email_with_attachment(to_email, subject, body, file_path):
    message = Mail(
        from_email="your_email@example.com",  # Replace with your verified SendGrid email
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
    to_email="recipient@example.com",  # Replace with the recipient's email
    subject="Here is your file",
    body="Please find the attached file.",
    file_path="/home/ubuntu/sample.csv"  # Change to your file path
)
