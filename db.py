import sqlite3
from datetime import datetime

DB_PATH = "db.sqlite3"


# ---------------------------------
# INIT DB + SEED DEFAULT DOMAINS
# ---------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS domain_labels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT UNIQUE,
        label TEXT,
        source TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

    seed_initial_domains()


# ---------------------------------
# INSERT / UPDATE DOMAIN → LABEL
# ---------------------------------
def save_domain_label(domain: str, label: str, source: str = "manual"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO domain_labels (domain, label, source, created_at)
    VALUES (?, ?, ?, ?)
    """, (domain.lower(), label, source, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()


# ---------------------------------
# GET LABEL FOR DOMAIN
# ---------------------------------
def get_domain_label(domain: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT label FROM domain_labels WHERE domain = ?", (domain.lower(),))
    row = cursor.fetchone()

    conn.close()
    return row[0] if row else None


# ---------------------------------
# GET ALL LABEL ROWS
# ---------------------------------
def get_all_labels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT domain, label, source FROM domain_labels")
    rows = cursor.fetchall()

    conn.close()
    return rows


# ---------------------------------
# DELETE DOMAIN
# ---------------------------------
def delete_domain(domain: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM domain_labels WHERE domain = ?", (domain.lower(),))
    conn.commit()
    conn.close()


# ---------------------------------
# SEED STATIC DOMAINS (one time)
# ---------------------------------
def seed_initial_domains():
    initial_domains = {
        # Entertainment
        "netflix.com": "Entertainment",
        "primevideo.com": "Entertainment",
        "hotstar.com": "Entertainment",
        "spotify.com": "Entertainment",
        "instagram.com": "Entertainment",
        "facebookmail.com": "Entertainment",
        "redditmail.com": "Entertainment",
        "pinterest.com": "Entertainment",

        # Shopping
        "amazon.in": "Shopping",
        "flipkart.com": "Shopping",
        "ajio.com": "Shopping",
        "myntra.com": "Shopping",

        # Food
        "zomato.com": "Food",
        "swiggy.com": "Food",

        # Travel
        "ola.com": "Travel",
        "uber.com": "Travel",
        "airindia.in": "Travel",
        "goindigo.in": "Travel",

        # Finance
        "hdfcbank.com": "Finance",
        "icicibank.com": "Finance",
        "axisbank.com": "Finance",
        "sbi.co.in": "Finance",
        "paytm.com": "Finance",

        # Career
        "linkedin.com": "Career",
        "naukri.com": "Career",
        "indeed.com": "Career",

        # Support
        "support.google.com": "Support",
        "support.microsoft.com": "Support",
    }

    for domain, label in initial_domains.items():
        save_domain_label(domain, label, source="seed")
