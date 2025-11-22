import os
import re
import json
import pickle

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest
from dotenv import load_dotenv
import google.generativeai as genai

# Local imports
from draft import generate_reply_and_save
from db import init_db, save_domain_label, get_domain_label, get_all_labels, delete_domain

# -----------------------------
# ENV + GEMINI CONFIG
# -----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

CLIENT_SECRETS_FILE = "client_secret_testing.json"
TOKEN_FILE = "token.pkl"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

# -----------------------------
# APP + DB INIT
# -----------------------------
app = FastAPI()
init_db()


# -----------------------------
# TOKEN HANDLING
# -----------------------------
def save_credentials(creds):
    with open(TOKEN_FILE, "wb") as f:
        pickle.dump(creds, f)


def load_credentials():
    if not os.path.exists(TOKEN_FILE):
        return None

    with open(TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        save_credentials(creds)

    return creds


# -----------------------------
# HELPERS
# -----------------------------
def extract_domain(email):
    if "@" in email:
        return email.split("@")[1].lower()
    return ""


def contains(text, keywords):
    text = text.lower()
    return any(k in text for k in keywords)


# -----------------------------
# RULE-BASED CLASSIFICATION
# -----------------------------
FIN_WORDS = ["invoice", "payment", "loan", "bank", "emi"]
BILL_WORDS = ["bill", "billing", "electricity"]
PROMO_WORDS = ["sale", "discount", "offer"]
TRAVEL_WORDS = ["flight", "booking", "itinerary"]
CAREER_WORDS = ["job", "hiring", "interview"]
WORK_WORDS = ["meeting", "update", "deadline"]

def rule_based(subject, sender):
    subject_l = subject.lower()
    sender_l = sender.lower()

    if contains(subject_l, FIN_WORDS):
        return "Finance", 90, "Rule-based: Finance"
    if contains(subject_l, BILL_WORDS):
        return "Bills", 90, "Rule-based: Bills"
    if contains(subject_l, PROMO_WORDS):
        return "Promotions", 85, "Rule-based: Promotions"
    if contains(subject_l, CAREER_WORDS):
        return "Career", 80, "Rule-based: Career"
    if contains(subject_l, WORK_WORDS):
        return "Work", 75, "Rule-based: Work"
    if contains(subject_l, TRAVEL_WORDS):
        return "Travel", 85, "Rule-based: Travel"

    if sender_l.endswith("@gmail.com"):
        return "Personal", 50, "Personal Gmail"

    return None, None, None


# -----------------------------
# AI ENTERTAINMENT FALLBACK
# -----------------------------
def ai_classify_domains(domains):
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    result_map = {}

    for i in range(0, len(domains), 20):
        batch = domains[i:i+20]

        prompt = f"""
Classify each domain as entertainment/social/dating or not.

Return ONLY JSON:
{{ 
 "results": [
   {{"domain": "...", "entertainment": true/false}}
 ]
}}

Domains: {batch}
"""
        try:
            out = model.generate_content(prompt)
            cleaned = out.text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned)

            for row in parsed["results"]:
                result_map[row["domain"]] = row["entertainment"]

        except:
            for d in batch:
                result_map[d] = False

    return result_map


# -----------------------------
# APPLY LABELS TO EMAILS
# -----------------------------
def apply_labels(service, user_id, messages, entertainment_cache):
    label_map = {
        lbl["name"].lower(): lbl["id"]
        for lbl in service.users().labels().list(userId=user_id).execute().get("labels", [])
    }

    def ensure_label(name):
        name_l = name.lower()
        if name_l in label_map:
            return label_map[name_l]

        new = service.users().labels().create(
            userId=user_id,
            body={"name": name}
        ).execute()

        label_map[name_l] = new["id"]
        return new["id"]

    results = {}

    for msg in messages:
        meta = service.users().messages().get(
            userId=user_id, id=msg["id"], format="metadata",
            metadataHeaders=["Subject", "From"]
        ).execute()

        headers = meta["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"]=="Subject"), "")
        sender_raw = next((h["value"] for h in headers if h["name"]=="From"), "")

        match = re.search(r"<([^>]+)>", sender_raw)
        sender = match.group(1) if match else sender_raw

        domain = extract_domain(sender)

        # 1) DB OVERRIDE
        db_label = get_domain_label(domain)
        if db_label:
            category = db_label
            conf = 99
            reason = "DB override"
        else:
            # 2) Rule-based
            category, conf, reason = rule_based(subject, sender)

            # 3) AI fallback
            if not category:
                if entertainment_cache.get(domain, False):
                    category = "Entertainment"
                    conf = 80
                    reason = "AI entertainment"
                else:
                    results[msg["id"]] = {"category": "None", "confidence": 0, "reason": "No rule matched"}
                    continue

        if category in ["Personal"]:
            results[msg["id"]] = {"category": "Personal (skipped)", "confidence": conf, "reason": reason}
            continue

        lbl_id = ensure_label(category)

        service.users().messages().modify(
            userId=user_id, id=msg["id"], body={"addLabelIds": [lbl_id]}
        ).execute()

        results[msg["id"]] = {"category": category, "confidence": conf, "reason": reason}

    return results


# -----------------------------
# ROUTES
# -----------------------------
@app.get("/")
def index():
    return HTMLResponse("""
        <h2>Welcome to Light MVP 🚀</h2>
        <p><a href='/login'>Login with Google</a></p>
        <p><a href='/domains'>Manage Domains</a></p>
    """)


# -----------------------------
# DOMAIN MANAGEMENT UI
# -----------------------------
@app.get("/domains")
def domains():
    rows = get_all_labels()

    html = """
    <h2>📁 Domain Label Management</h2>
    <a href='/'>← Back</a><br><br>

    <table border='1' cellpadding='6'>
        <tr><th>Domain</th><th>Label</th><th>Source</th><th>Action</th></tr>
    """

    for domain, label, source in rows:
        html += f"""
        <tr>
            <td>{domain}</td>
            <td>{label}</td>
            <td>{source}</td>
            <td><a href='/delete_domain?domain={domain}'>Delete</a></td>
        </tr>
        """

    html += """
    </table>
    <br><br>

    <h3>Add / Update Domain</h3>
    <form action='/save_domain' method='GET'>
        Domain: <input name='domain' required>
        Label: <input name='label' required>
        <button type='submit'>Save</button>
    </form>
    """

    return HTMLResponse(html)


@app.get("/save_domain")
def save_domain(domain: str, label: str):
    save_domain_label(domain, label, source="manual")
    return RedirectResponse("/domains", status_code=302)


@app.get("/delete_domain")
def delete_domain_route(domain: str):
    delete_domain(domain)
    return RedirectResponse("/domains", status_code=302)


# -----------------------------
# LOGIN + OAUTH
# -----------------------------
@app.get("/login")
def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        SCOPES,
        redirect_uri="http://localhost:8080/oauth2callback"
    )
    url, _ = flow.authorization_url(prompt="consent", include_granted_scopes="true")
    return RedirectResponse(url)


@app.get("/oauth2callback")
def oauth_callback(request: Request):
    state = request.query_params.get("state")

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        SCOPES,
        state=state,
        redirect_uri="http://localhost:8080/oauth2callback"
    )

    flow.fetch_token(authorization_response=str(request.url))
    save_credentials(flow.credentials)

    service = build("gmail", "v1", credentials=flow.credentials)
    email = service.users().getProfile(userId="me").execute()["emailAddress"]

    # Collect domains from 100 messages
    messages_100 = service.users().messages().list(
        userId="me", maxResults=100
    ).execute().get("messages", [])

    domains = set()
    for msg in messages_100:
        data = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata", metadataHeaders=["From"]
        ).execute()

        fr = next((h["value"] for h in data["payload"]["headers"] if h["name"]=="From"), "")
        m = re.search(r"<([^>]+)>", fr)
        pure = m.group(1) if m else fr

        domains.add(extract_domain(pure))

    entertainment_cache = ai_classify_domains(list(domains))

    # Label last 20 messages
    last20 = service.users().messages().list(
        userId="me", maxResults=20
    ).execute().get("messages", [])

    results = apply_labels(service, "me", last20, entertainment_cache)

    html = f"<h2>Logged in as {email}</h2>"
    html += "<p><a href='/draft_all'>Generate Auto Replies</a></p><br>"
    html += "<h3>🏷 Label Results</h3>"

    for mid, info in results.items():
        html += f"<p><b>{mid}</b> → {info['category']} ({info['confidence']}%)<br>{info['reason']}</p>"

    return HTMLResponse(html)


# -----------------------------
# SINGLE MESSAGE DRAFT
# -----------------------------
@app.get("/draft/{message_id}")
def draft_reply(message_id: str):
    creds = load_credentials()
    if not creds:
        return {"error": "Login again"}

    service = build("gmail", "v1", credentials=creds)

    message = service.users().messages().get(
        userId="me", id=message_id, format="full"
    ).execute()

    return generate_reply_and_save(service, message)


# -----------------------------
# AUTO DRAFT LAST 20 EMAILS
# -----------------------------
@app.get("/draft_all")
def draft_all():
    creds = load_credentials()
    if not creds:
        return {"error": "Login again"}

    service = build("gmail", "v1", credentials=creds)

    last20 = service.users().messages().list(
        userId="me", maxResults=20
    ).execute().get("messages", [])

    drafted, skipped = [], []

    for msg in last20:
        full = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()

        res = generate_reply_and_save(service, full)

        if res.get("eligible"):
            drafted.append(res)
        else:
            skipped.append(res)

    return {
        "processed": len(last20),
        "drafted": drafted,
        "skipped": skipped
    }
