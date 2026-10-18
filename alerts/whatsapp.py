from twilio.rest import Client
import time
from datetime import datetime

# =========================
# TWILIO CREDENTIALS
# =========================
ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
AUTH_TOKEN  = "YOUR_TWILIO_AUTH_TOKEN"

FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP   = "whatsapp:+918281871363"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# =========================
# COOLDOWN
# =========================
_last_alert_time = 0
COOLDOWN_SECONDS = 30

def send_whatsapp_alert(
    camera_id,
    threat_type,
    confidence=None,
    timestamp=None,
    image_url=None
):
    global _last_alert_time

    now = time.time()
    if now - _last_alert_time < COOLDOWN_SECONDS:
        return

    _last_alert_time = now

    if timestamp is None:
        timestamp = datetime.now()

    date_str = timestamp.strftime("%d-%m-%Y")
    time_str = timestamp.strftime("%H:%M:%S")

    body = (
        f"🚨 CCTV THREAT ALERT 🚨\n\n"
        f"📍 Camera ID: {camera_id}\n"
        f"⚠️ Threat: {threat_type}\n"
        f"📅 Date: {date_str}\n"
        f"⏰ Time: {time_str}\n"
    )

    if confidence is not None:
        body += f"📊 Confidence: {confidence:.2f}\n"

    try:
        msg = client.messages.create(
            body=body,
            from_=FROM_WHATSAPP,
            to=TO_WHATSAPP,
            media_url=[image_url] if image_url else None
        )
        print("✅ WhatsApp alert sent with snapshot:", msg.sid)

    except Exception as e:
        print("❌ WhatsApp alert failed:", e)
