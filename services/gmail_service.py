#import os.path
#import base64
#from email import message_from_bytes

#from google.oauth2.credentials import Credentials
#from google_auth_oauthlib.flow import InstalledAppFlow
#from google.auth.transport.requests import Request
#from googleapiclient.discovery import build

#SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

#def get_gmail_service():
    #creds = None

    #if os.path.exists('token.json'):
        #creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    #if not creds or not creds.valid:
        #if creds and creds.expired and creds.refresh_token:
            #creds.refresh(Request())
        #else:
            #flow = InstalledAppFlow.from_client_secrets_file(
                #'credentials.json', SCOPES)
            #creds = flow.run_local_server(port=0)

        #with open('token.json', 'w') as token:
            #token.write(creds.to_json())

    #service = build('gmail', 'v1', credentials=creds)
    #return service


#def fetch_unread_rfq_replies():
    #service = get_gmail_service()

    # Search unread mails containing RFQ
    #results = service.users().messages().list(
        #userId='me',
        #q='is:unread subject:RFQ'
    #).execute()

    #messages = results.get('messages', [])

    #emails = []

    #if not messages:
        #return emails

    #for msg in messages:
        #msg_data = service.users().messages().get(
            #userId='me',
            #id=msg['id'],
            #format='raw'
        #).execute()

        #raw_data = base64.urlsafe_b64decode(msg_data['raw'])
        #email_message = message_from_bytes(raw_data)

        #subject = email_message['Subject']
        #from_email = email_message['From']

        #body = ""

        #if email_message.is_multipart():
            #for part in email_message.walk():
                #if part.get_content_type() == "text/plain":
                    #body = part.get_payload(decode=True).decode()
        #else:
            #body = email_message.get_payload(decode=True).decode()

        #emails.append({
            #"id": msg['id'],
            #"subject": subject,
            #"from": from_email,
            #"body": body
        #})

        # Mark as read
        #service.users().messages().modify(
            #userId='me',
            #id=msg['id'],
            #body={'removeLabelIds': ['UNREAD']}
        #).execute()

    #return emails

import base64
import re
import sqlite3
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from services.openai_service import extract_vendor_quote

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# ==============================
# GMAIL CONNECTION
# ==============================
def get_gmail_service():

    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


# ==============================
# SIMPLE TEXT EXTRACTOR
# ==============================
def extract_details_from_text(text):

    unit_price = None
    delivery_days = None
    payment_terms = None

    # Basic regex (can improve later)
    price_match = re.search(r'(\d+\.?\d*)', text)
    if price_match:
        unit_price = float(price_match.group(1))

    delivery_match = re.search(r'(\d+)\s*days', text.lower())
    if delivery_match:
        delivery_days = delivery_match.group(1)

    if "advance" in text.lower():
        payment_terms = "Advance"
    elif "credit" in text.lower():
        payment_terms = "Credit"

    return unit_price, delivery_days, payment_terms


# ==============================
# FETCH RFQ RELATED REPLIES
# ==============================
def fetch_rfq_replies():

    service = get_gmail_service()

    # Search only RFQ related threads
    results = service.users().messages().list(
        userId="me",
        q="subject:RFQ"
    ).execute()

    messages = results.get("messages", [])

    conn = sqlite3.connect("procurement.db")
    cursor = conn.cursor()

    for msg in messages:

        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        headers = msg_data["payload"]["headers"]

        subject = ""
        sender = ""
        thread_id = msg_data["threadId"]

        for header in headers:
            if header["name"] == "Subject":
                subject = header["value"]
            if header["name"] == "From":
                sender = header["value"]

        # Get email body
        parts = msg_data["payload"].get("parts", [])
        body = ""

        if parts:
            for part in parts:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(
                        part["body"]["data"]
                    ).decode("utf-8")
        else:
            body = base64.urlsafe_b64decode(
                msg_data["payload"]["body"]["data"]
            ).decode("utf-8")

        # Extract info
        unit_price, delivery_days, payment_terms = extract_details_from_text(body)

        
        # Extract structured data using GPT
        extracted = extract_vendor_quote(body)

        unit_price = extracted.get("unit_price")
        delivery_days = extracted.get("delivery_days")
        payment_terms = extracted.get("payment_terms")
        # Update rfq_vendors table
        cursor.execute("""
            UPDATE rfq_vendors
            SET status = ?,
                thread_id = ?,
                reply_date = datetime('now'),
                extracted_unit_price = ?,
                extracted_delivery_days = ?,
                extracted_payment_terms = ?,
                raw_reply = ?
            WHERE vendor_email = ?
        """, (
            "Replied",
            thread_id,
            unit_price,
            delivery_days,
            payment_terms,
            email_body,
            vendor_email
        ))

    conn.commit()
    conn.close()

    print("RFQ replies synced successfully.")