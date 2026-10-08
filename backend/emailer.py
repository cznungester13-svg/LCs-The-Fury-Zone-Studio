import os
import asyncio
import logging
try:
    import resend
except ImportError:
    resend = None

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, html: str):
    api_key = os.environ.get("RESEND_API_KEY", "")
    if not api_key or resend is None:
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


def _shell(body: str) -> str:
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:560px;margin:auto">
      <div style="background:#0A0A0A;color:#fff;padding:24px"><h1 style="margin:0;color:#FF3B30">LCs THE FURY ZONE</h1></div>
      <div style="padding:24px">{body}</div>
    </div>"""


def welcome_html(name: str) -> str:
    from html import escape
    return _shell(f"""
        <h2>Welcome to the Zone, {escape(name or 'friend')}! \U0001F525</h2>
        <p>Your account is live. As a new shopper you've got a
           <b style="color:#FF3B30">New Shopper Bonus</b> waiting:
           your <b>3 cheapest items are FREE</b> at checkout.</p>
        <p>Fresh drops land weekly across 17 departments \u2014 come grab the deals.</p>
    """)


def newsletter_html() -> str:
    return _shell("""
        <h2>You're on the list! \u26A1</h2>
        <p>Thanks for subscribing. You'll be first to hear about new drops,
           flash deals and exclusive codes at The Fury Zone.</p>
    """)
