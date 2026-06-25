"""
Flask webhook server.
Twilio sends incoming WhatsApp messages here via HTTP POST.
"""

from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

import game_state
import game_master

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    phone      = request.form.get("From", "")       # e.g. whatsapp:+919876543210
    body       = request.form.get("Body", "").strip()
    num_media  = int(request.form.get("NumMedia", 0))
    media_url  = request.form.get("MediaUrl0", None)  # first attached image

    team = game_state.get_or_create(phone)

    # ── Determine reply ────────────────────────────────────────────────────
    if not team.registered:
        reply = game_master.handle_registration(team, body)

    elif num_media > 0 and media_url:
        reply = game_master.handle_photo(team, media_url)

    else:
        # Re-check registration flow (team_name step)
        reg_reply = game_master.handle_registration(team, body)
        if reg_reply:
            reply = reg_reply
        else:
            reply = game_master.handle_text(team, body)

    # ── Send back via Twilio TwiML ─────────────────────────────────────────
    resp = MessagingResponse()
    resp.message(reply)
    return Response(str(resp), mimetype="application/xml")


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    """Simple HTML leaderboard you can open in browser."""
    rows = game_state.all_teams_summary()
    html = "<h2>🏆 Live Leaderboard</h2><table border=1 cellpadding=8>"
    html += "<tr><th>Rank</th><th>Team</th><th>Score</th><th>Checkpoints</th></tr>"
    for i, t in enumerate(rows, 1):
        html += f"<tr><td>{i}</td><td>{t['name']}</td><td>{t['score']}</td><td>{t['completed']}</td></tr>"
    html += "</table>"
    return html


@app.route("/", methods=["GET"])
def home():
    return "Hunt Master is LIVE. 🎯"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
