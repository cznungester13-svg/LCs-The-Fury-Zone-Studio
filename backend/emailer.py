import os
import asyncio
import logging
import resend

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, html: str):
    api_key = os.environ.get("RESEND_API_KEY", "")
    if not api_key:
        logger.info(f"[email skipped - no RESEND_API_KEY] to={to} subject={subject}")
        return {"status": "skipped"}
        
    resend.api_key = api_key
    params = {
        "from": os.environ.get("SENDER_EMAIL", "onboarding@resend.dev"),
        "to": [to],
        "subject": subject,
        "html": html,
    }
    try:
        # Fix: Safely execute the blocking SDK call on an off-loop worker thread
        email = await asyncio.to_thread(resend.Emails.send, params)
        # Fix: Access the response identifier as an object attribute, not via .get()
        return {"status": "success", "id": getattr(email, "id", None)}
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return {"status": "error", "error": str(e)}


def order_confirmation_html(order: dict) -> str:
    rows = "".join(
        f"<tr><td style='padding:8px;border-bottom:1px solid #eee'>{i['title']} x{i['quantity']}</td>"
        f"<td style='padding:8px;border-bottom:1px solid #eee;text-align:right'>${i['price']*i['quantity']:.2f}</td></tr>"
        for i in order.get("items", [])
    )
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:560px;margin:auto">
      <div style="background:#0A0A0A;color:#fff;padding:24px"><h1 style="margin:0;color:#FF3B30">LCs THE FURY ZONE</h1></div>
      <div style="padding:24px">
        <h2>Order Confirmed</h2>
        <p>Thanks for your order <b>#{order['id'][:8]}</b>. We're on it.</p>
        <table style="width:100%;border-collapse:collapse">{rows}</table>
        <p style="text-align:right;font-size:18px\"><b>Total: ${order['total']:.2f}</b></p>
      </div>
    </div>"""
