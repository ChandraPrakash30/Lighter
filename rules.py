# rules.py

import re

# -------------------------------
# CATEGORY LIST (STRICT CONTROL)
# -------------------------------
CATEGORIES = [
    "Finance",
    "Bills",
    "Promotions/Offers",
    "Career",
    "Work",
    "Personal",
    "Travel",
    "Newsletter",
    "Support",
    "Urgent",
    "Entertainment",
    "Others"
]

# -------------------------------
# KEYWORD GROUPS
# -------------------------------

FINANCE_WORDS = [
    "invoice", "payment", "receipt", "credit card", "loan", "emi",
    "bank", "statement", "transaction", "upi", "debit", "credit"
]

BILL_WORDS = ["bill", "billing", "electricity", "gas", "water", "mobile bill"]

PROMOTION_WORDS = [
    "sale", "discount", "offer", "deal", "limited time",
    "coupon", "free", "clearance"
]

CAREER_WORDS = ["job", "hiring", "interview", "recruiter", "opportunity"]

WORK_WORDS = ["meeting", "update", "deadline", "project"]

TRAVEL_WORDS = ["flight", "ticket", "booking", "itinerary"]

SUPPORT_WORDS = ["support", "helpdesk", "noreply@support"]

URGENT_WORDS = ["urgent", "alert", "action required"]

ENTERTAINMENT_HINTS = [
    "netflix", "hotstar", "spotify", "prime", "youtube",
    "instagram", "facebook", "reddit", "pinterest"
]


# --------------------------------------------------------------
# RULE-BASED CLASSIFICATION (STRICT + CONTROLLED)
# --------------------------------------------------------------

def rule_based_classify(subject: str, sender: str):
    """
    Returns:
        category, confidence, reason
        OR
        ("UNKNOWN_CHECK_ENTERTAINMENT", 40, ...) → means AI must verify domain
    """

    subject_l = subject.lower()
    sender_l = sender.lower()

    # -----------------------
    # FINANCE
    # -----------------------
    if any(w in subject_l or w in sender_l for w in FINANCE_WORDS):
        return "Finance", 90, "Rule-based: Finance keywords matched"

    # -----------------------
    # BILLS
    # -----------------------
    if any(w in subject_l or w in sender_l for w in BILL_WORDS):
        return "Bills", 90, "Rule-based: Bill keywords matched"

    # -----------------------
    # PROMOTIONS
    # -----------------------
    if any(w in subject_l for w in PROMOTION_WORDS):
        return "Promotions/Offers", 85, "Rule-based: Promotion keywords matched"

    # -----------------------
    # CAREER
    # -----------------------
    if any(w in subject_l for w in CAREER_WORDS):
        return "Career", 85, "Rule-based: Career keywords matched"

    # -----------------------
    # WORK (meetings, deadlines, projects)
    # -----------------------
    if any(w in subject_l for w in WORK_WORDS):
        return "Work", 80, "Rule-based: Work keyword matched"

    # -----------------------
    # TRAVEL
    # -----------------------
    if any(w in subject_l for w in TRAVEL_WORDS):
        return "Travel", 85, "Rule-based: Travel keyword matched"

    # -----------------------
    # SUPPORT
    # -----------------------
    if any(w in sender_l for w in SUPPORT_WORDS):
        return "Support", 70, "Rule-based: Support sender"

    # -----------------------
    # URGENT
    # -----------------------
    if any(w in subject_l for w in URGENT_WORDS):
        return "Urgent", 90, "Rule-based: Urgent keyword"

    # -----------------------
    # NEWSLETTER
    # (Detected but NOT applied — main.py will skip)
    # -----------------------
    if "newsletter" in sender_l or "digest" in sender_l:
        return "Newsletter", 60, "Rule-based: Newsletter sender detected"

    # -----------------------
    # PERSONAL — detected but NOT applied
    # -----------------------
    if sender_l.endswith("@gmail.com"):
        # Exclude obvious businesses
        blocked = ["amazon", "flipkart", "zomato", "swiggy", "ola"]
        if not any(b in sender_l for b in blocked):
            return "Personal", 50, "Rule-based: Gmail personal sender"

    # -----------------------
    # DIRECT ENTERTAINMENT DOMAINS
    # -----------------------
    if any(hint in sender_l for hint in ENTERTAINMENT_HINTS):
        return "Entertainment", 95, "Rule-based: Known entertainment platform"

    # -----------------------
    # UNKNOWN → Send to Gemini to check ONLY entertainment domain
    # -----------------------
    return "UNKNOWN_CHECK_ENTERTAINMENT", 40, "Possible entertainment domain — AI check needed"
