import base64
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import google.generativeai as genai


# --------------------------
# CLEAN HTML → PLAIN TEXT
# --------------------------
def clean_html(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n").strip()
    except:
        return html


# --------------------------
# EXTRACT HEADER BY NAME
# --------------------------
def get_header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


# --------------------------
# CHECK IF EMAIL IS < 24 HOURS OLD
# --------------------------
def is_recent(date_string):
    try:
        email_date = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")
        diff = datetime.now(email_date.tzinfo) - email_date
        return diff.total_seconds() <= 86400
    except:
        return False


# --------------------------
# GENERATE AI REPLY
# --------------------------
def generate_ai_reply(thread_text):
    model = genai.GenerativeModel("models/gemini-2.5-flash")



    prompt = f"""
You are an assistant that drafts professional and natural email replies.

Below is the full email thread. Summaries and clean replies are allowed. 
Do NOT hallucinate details. Maintain the same tone and context.

THREAD:
{thread_text}

Write a helpful reply:
"""

    response = model.generate_content(prompt)
    return response.text.strip()


# --------------------------
# CREATE GMAIL DRAFT
# --------------------------
def create_gmail_draft(service, user_id, to_email, subject, reply_text, thread_id):
    message = MIMEText(reply_text, "plain")
    message["To"] = to_email
    message["Subject"] = "Re: " + subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft_body = {
        "message": {
            "raw": raw,
            "threadId": thread_id
        }
    }

    draft = service.users().drafts().create(userId=user_id, body=draft_body).execute()
    return draft


# --------------------------
# MAIN ENGINE USED BY main.py
# --------------------------
def generate_reply_and_save(service, message_full):
    """
    message_full = Gmail message fetched with format="full"
    """

    headers = message_full["payload"]["headers"]

    from_field = get_header(headers, "From")
    subject = get_header(headers, "Subject")
    date_str = get_header(headers, "Date")
    thread_id = message_full.get("threadId")

    # -------------------------------
    # RULE 1: Sender must be @gmail.com
    # -------------------------------
    if "@gmail.com" not in from_field:
        return {"eligible": False, "reason": "Sender not gmail.com"}

    # -------------------------------
    # RULE 2: Only reply if < 24 hours old
    # -------------------------------
    if not is_recent(date_str):
        return {"eligible": False, "reason": "Email older than 24 hours"}

    # -------------------------------
    # Extract the HTML body
    # -------------------------------
    def extract_body(payload):
        if "body" in payload and "data" in payload["body"]:
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
        if "parts" in payload:
            for p in payload["parts"]:
                result = extract_body(p)
                if result:
                    return result
        return ""

    html_body = extract_body(message_full["payload"])
    plain_text = clean_html(html_body)

    # -------------------------------
    # Generate AI reply
    # -------------------------------
    reply_text = generate_ai_reply(plain_text)

    # -------------------------------
    # Create Gmail draft
    # -------------------------------
    draft = create_gmail_draft(
        service=service,
        user_id="me",
        to_email=from_field,
        subject=subject,
        reply_text=reply_text,
        thread_id=thread_id
    )

    return {
        "eligible": True,
        "draft_id": draft["id"],
        "reply_preview": reply_text[:200] + "..."
    }
