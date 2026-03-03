from openai import OpenAI

client = OpenAI(api_key="OPEN_API_KEY")



def extract_vendor_quote(email_text):
    """
    Extract structured RFQ details from vendor email reply
    """

    prompt = f"""
    You are an AI procurement assistant.

    Extract the following details from this vendor email reply:

    1. unit_price (number only)
    2. delivery_days (number only)
    3. payment_terms (text)

    If any field is missing, return null.

    Reply ONLY in valid JSON format like:
    {{
        "unit_price": 25.5,
        "delivery_days": 15,
        "payment_terms": "30% advance, balance before dispatch"
    }}

    Email:
    {email_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    try:
        extracted = json.loads(response.choices[0].message.content)
        return extracted
    except:
        return {
            "unit_price": None,
            "delivery_days": None,
            "payment_terms": None
        }