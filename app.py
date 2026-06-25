"""
Flask webhook server.
Twilio sends incoming WhatsApp messages here via HTTP POST.

Photo processing happens in a background thread so we always reply
to Twilio within its 15-second timeout window.
"""

import threading
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

import game_state
import game_master
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUM

app = Flask(__name__)


def send_message(to_number: str, body: str):
    """Send a WhatsApp message via Twilio REST API (used for async replies)."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        from_=TWILIO_WHATSAPP_NUM,
        to=to_number,
        body=body,
    )


def process_photo_async(phone: str, media_url: str):
    """Validate photo in background thread, then send result via Twilio API."""
    try:
        team = game_state.get_or_create(phone)
        reply = game_master.handle_photo(team, media_url)
        send_message(phone, reply)
    except Exception as e:
        send_message(phone, f"⚠️ Error processing photo. Please try again.")


@app.route("/webhook", methods=["POST"])
def webhook():
    phone     = request.form.get("From", "")
    body      = request.form.get("Body", "").strip()
    num_media = int(request.form.get("NumMedia", 0))
    media_url = request.form.get("MediaUrl0", None)

    team = game_state.get_or_create(phone)

    if not team.registered:
        reply = game_master.handle_registration(team, body)
        return _twiml_reply(reply)

    if num_media > 0 and media_url:
        # Reply immediately so Twilio doesn't timeout, process photo in background
        threading.Thread(
            target=process_photo_async,
            args=(phone, media_url),
            daemon=True,
        ).start()
        return _twiml_reply("📸 Photo received. Analysing... please wait.")

    # Text message
    reg_reply = game_master.handle_registration(team, body)
    if reg_reply:
        return _twiml_reply(reg_reply)

    reply = game_master.handle_text(team, body)
    return _twiml_reply(reply)


def _twiml_reply(text: str) -> Response:
    resp = MessagingResponse()
    resp.message(text)
    return Response(str(resp), mimetype="application/xml")


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    rows = game_state.all_teams_summary()
    html = "<h2>Live Leaderboard</h2><table border=1 cellpadding=8>"
    html += "<tr><th>Rank</th><th>Team</th><th>Score</th><th>Checkpoints</th></tr>"
    for i, t in enumerate(rows, 1):
        html += f"<tr><td>{i}</td><td>{t['name']}</td><td>{t['score']}</td><td>{t['completed']}</td></tr>"
    html += "</table>"
    return html


@app.route("/", methods=["GET"])
def home():
    return "Hunt Master is LIVE."


if __name__ == "__main__":
    app.run(debug=True, port=5000)
