import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "GMAIL_EMAIL"
SENDER_PASSWORD = "GMAIL_APP_PASSWORD"


def send_rfq_email(to_email, vendor_name, project_id, material_name, quantity, rfq_id):

    subject = f"RFQ-{rfq_id} | {project_id} | {material_name}""

    body = f"""
Dear {vendor_name},

We request you to submit your quotation for the following material:

Project: {project_id}
Material: {material_name}
Required Quantity: {quantity}

Kindly provide:
- Unit Price
- Total Price
- Delivery Timeline
- Payment Terms

Please reply to this email only with your quotation.

"""

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Email error:", e)
        return False