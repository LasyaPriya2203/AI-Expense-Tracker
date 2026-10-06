import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY) if API_KEY else None


def categorize_expense(description, merchant="", amount=0):

    if not client:
        return {
            "category": "Other",
            "reason": "OpenAI API key not configured."
        }

    prompt = f"""
You are an AI expense categorization assistant.

Expense:
Merchant: {merchant}
Amount: ₹{amount}
Description: {description}

Choose exactly one category:

Food
Transportation
Groceries
Shopping
Rent
Utilities
Education
Healthcare
Entertainment
Travel
Subscriptions
Other

Return ONLY JSON:

{{
    "category": "Food",
    "reason": "Short explanation"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You classify personal expenses."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        return json.loads(
            response.choices[0].message.content
        )

    except Exception as e:
        return {
            "category": "Other",
            "reason": str(e)
        }


def generate_insights(expense_text):

    if not client:
        return "OpenAI API key is not configured."

    prompt = f"""
Analyze these personal expenses:

{expense_text}

Provide:

1. Total spending observation
2. Highest spending category
3. Spending problems
4. Ways to save money
5. Three practical recommendations

Keep the answer simple.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a personal finance assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI error: {e}"


def ask_ai(question, expense_text):

    if not client:
        return "Please configure your OPENAI_API_KEY."

    prompt = f"""
You are an AI expense assistant.

Expense data:

{expense_text}

User question:

{question}

Answer only using the available expense data.
Do not invent information.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an accurate financial assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI error: {e}"


def analyze_receipt(image):

    if not client:
        return {
            "merchant": "",
            "amount": 0,
            "category": "Other",
            "date": "",
            "description": ""
        }

    try:

        import base64

        image_bytes = image.getvalue()

        base64_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You extract information from receipts."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
Extract receipt information.

Return ONLY JSON:

{
    "merchant": "",
    "amount": 0,
    "category": "",
    "date": "",
    "description": ""
}
"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )

        return json.loads(
            response.choices[0].message.content
        )

    except Exception as e:

        return {
            "merchant": "",
            "amount": 0,
            "category": "Other",
            "date": "",
            "description": str(e)
        }