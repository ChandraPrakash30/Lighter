# classify_ai.py

import os
import json
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def ai_check_entertainment(domain: str) -> bool:
    """
    Uses Gemini to classify if a domain belongs to entertainment/social/dating apps.
    IMPORTANT:
        - Returns ONLY True / False
        - Does NOT return categories
        - Safe JSON extraction
    """

    model = genai.GenerativeModel("models/gemini-2.5-flash")


    prompt = f"""
You are a domain classifier.

Classify ONLY whether this domain belongs to **entertainment, social media, or dating apps**.

Entertainment examples:
- Dating: tinder, bumble, hinge
- Social: instagram, facebook, reddit, pinterest
- Video/Music: netflix, primevideo, youtube, spotify

DOMAIN: "{domain}"

Respond ONLY as valid JSON:
{{
  "entertainment": true/false
}}
"""

    try:
        response = model.generate_content(prompt)

        # Clean model output
        raw = response.text.strip()

        # Remove markdown code blocks if present
        raw = raw.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw)

        return data.get("entertainment", False)

    except Exception as e:
        # If AI fails → default to False (safe)
        return False
