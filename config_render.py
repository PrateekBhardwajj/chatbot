"""
This file is used on Render (cloud). Keys come from Render environment variables.
Rename this to config.py on the server, OR Render uses this via the start command.
"""
import os

DEEPSEEK_API_KEY    = os.environ.get("DEEPSEEK_API_KEY", "")
GEMINI_API_KEY      = os.environ.get("GEMINI_API_KEY", "")
TWILIO_ACCOUNT_SID  = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN   = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUM = os.environ.get("TWILIO_WHATSAPP_NUM", "whatsapp:+14155238886")

GOOGLE_SHEET_ID = ""
GAME_NAME       = "Digital Amazing Race"
HUNT_MASTER     = "The Hunt Master"
