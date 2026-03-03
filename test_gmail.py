from services.gmail_service import fetch_rfq_replies

emails = fetch_rfq_replies()

print("Emails Found:")
for e in emails:
    print(e["subject"])
    print(e["from"])
    print("------")