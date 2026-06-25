"""
Core AI logic – uses Google Gemini (free tier) for text replies and photo validation.
"""

import base64
import time
import ssl
import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from config import GEMINI_API_KEY


# SSL verification disabled for local Windows testing (works fine on cloud deployment)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_session = requests.Session()
_session.verify = False


def _post(url, **kwargs):
    """POST with automatic retry on 429 rate limit."""
    for attempt in range(3):
        r = _session.post(url, **kwargs)
        if r.status_code == 429:
            wait = 15 * (attempt + 1)   # 15s, 30s, 45s
            print(f"Gemini 429 rate limit — waiting {wait}s (attempt {attempt+1})")
            time.sleep(wait)
            continue
        return r
    r.raise_for_status()
    return r
from challenges import CHALLENGE_MAP, TOTAL_CHALLENGES

GEMINI_TEXT_URL   = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
GEMINI_VISION_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """
You are The Hunt Master — the mysterious, dramatic host of the Digital Amazing Race.

Rules you ALWAYS follow:
- Speak in short, punchy, immersive sentences. Use emojis sparingly but effectively.
- Never reveal future clues unless the team has unlocked them.
- If a team seems stuck, offer a cryptic hint — never the full answer outright.
- Address teams as "Agent" or by their team name.
- Keep every response under 80 words.
- When awarding points, always state the exact score clearly.
- If someone asks something off-topic, stay in character: "The Hunt Master does not deal in distractions."
"""


def _chat(messages: list[dict]) -> str:
    # Build Gemini contents format
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 300, "temperature": 0.7},
    }
    r = _post(GEMINI_TEXT_URL, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


def _validate_photo_with_vision(image_url: str, question: str) -> bool:
    """Download image from Twilio, send to Gemini Vision for validation."""
    from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
    img_response = _session.get(image_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=20)
    img_b64 = base64.b64encode(img_response.content).decode("utf-8")
    mime     = img_response.headers.get("Content-Type", "image/jpeg")

    payload = {
        "contents": [
            {
                "parts": [
                    {"inline_data": {"mime_type": mime, "data": img_b64}},
                    {"text": question + " Answer YES or NO only."},
                ]
            }
        ],
        "generationConfig": {"maxOutputTokens": 5, "temperature": 0},
    }
    r = _post(GEMINI_VISION_URL, json=payload, timeout=30)
    r.raise_for_status()
    answer = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
    return answer.startswith("YES")


# ── Public functions called by app.py ──────────────────────────────────────

def handle_registration(team, text: str) -> str:
    """First interaction – ask for team name."""
    if not team.registered:
        if team.waiting_for == "team_name":
            team.name       = text.strip().title()
            team.registered = True
            team.waiting_for = None
            challenge = CHALLENGE_MAP[1]
            return (
                f"🎯 Identity confirmed. Welcome, *{team.name}*!\n\n"
                f"The race begins NOW.\n\n"
                f"{challenge['clue']}"
            )
        else:
            team.waiting_for = "team_name"
            return (
                "🕵️ *IDENTITY REQUIRED*\n\n"
                "State your team name, Agent.\n"
                "No name, no mission."
            )
    return None   # already registered, caller handles


def handle_photo(team, image_url: str) -> str:
    if not team.registered:
        return "Identify yourself first. Send your team name."

    challenge = CHALLENGE_MAP.get(team.current_clue)
    if not challenge:
        return "🏆 All missions complete. Await final debrief."

    if challenge["type"] != "photo":
        return "⚠️ This checkpoint does not require a photo. Read your mission brief again."

    passed = _validate_photo_with_vision(image_url, challenge["validate"])

    if passed:
        team.score       += challenge["points"]
        team.completed.append(challenge["id"])
        team.current_clue += 1

        if team.current_clue > TOTAL_CHALLENGES:
            return (
                f"✅ *CHALLENGE {challenge['id']} COMPLETE!*\n"
                f"*+{challenge['points']} points* | Total: *{team.score} pts*\n\n"
                f"🏆 *ALL MISSIONS COMPLETE, {team.name}!*\n"
                f"Report to HQ. Your final score: *{team.score} pts*."
            )

        next_challenge = CHALLENGE_MAP[team.current_clue]
        return (
            f"✅ *CHALLENGE {challenge['id']} COMPLETE!*\n"
            f"*+{challenge['points']} points* | Total: *{team.score} pts*\n\n"
            f"{next_challenge['clue']}"
        )
    else:
        return (
            f"❌ *VALIDATION FAILED.*\n"
            f"That is not what the Hunt Master seeks.\n"
            f"Try again. Mission: _{challenge['task']}_"
        )


def handle_text(team, text: str) -> str:
    text_lower = text.lower().strip()

    # Special commands
    if any(w in text_lower for w in ["hint", "help", "stuck", "clue"]):
        challenge = CHALLENGE_MAP.get(team.current_clue)
        if challenge:
            return f"🔎 *HINT:* _{challenge['hint']}_\n\nNo more hints for this checkpoint."
        return "You have completed all missions. No hints needed."

    if any(w in text_lower for w in ["score", "points", "how many"]):
        return f"📊 *{team.name}* | Score: *{team.score} pts* | Checkpoints done: *{len(team.completed)}/{TOTAL_CHALLENGES}*"

    if any(w in text_lower for w in ["current", "mission", "task", "what"]):
        challenge = CHALLENGE_MAP.get(team.current_clue)
        if challenge:
            return f"📋 *CURRENT MISSION:*\n\n{challenge['clue']}"
        return "All missions complete."

    # General AI reply in character
    team.message_history.append({"role": "user", "content": text})
    reply = _chat(team.message_history[-6:])   # last 6 messages for context
    team.message_history.append({"role": "assistant", "content": reply})
    return reply
