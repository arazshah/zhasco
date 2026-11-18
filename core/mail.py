"""Company mailbox helpers: IMAP sync into MailMessage and SMTP sending."""
import imaplib
import logging
import re
from datetime import timezone as dt_timezone
from email import message_from_bytes, policy
from email.utils import parseaddr, parsedate_to_datetime

import nh3
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from core.models import MailMessage, MailSync

log = logging.getLogger(__name__)
FIRST_SYNC_LIMIT = 100
MAX_BODY = 200_000
# no <img>/<style>/<script>/forms: avoids tracking pixels and active content in received mail
SAFE_TAGS = {"p", "br", "b", "strong", "i", "em", "u", "ul", "ol", "li", "blockquote", "a", "div", "span",
             "table", "thead", "tbody", "tr", "td", "th", "h1", "h2", "h3", "h4", "pre", "hr"}


class MailError(Exception):
    pass


def configured():
    return bool(settings.MAIL_USER and settings.MAIL_PASSWORD)


def _clean(html):
    return nh3.clean(html[:MAX_BODY], tags=SAFE_TAGS, attributes={"a": {"href"}}, link_rel="noopener noreferrer",
                     url_schemes={"http", "https", "mailto"})


def _parse(raw, uid):
    msg = message_from_bytes(raw, policy=policy.default)
    name, addr = parseaddr(str(msg.get("From", "")))
    try:
        when = parsedate_to_datetime(str(msg.get("Date")))
        if when.tzinfo is None:
            when = when.replace(tzinfo=dt_timezone.utc)
    except Exception:
        when = timezone.now()
    text_part = msg.get_body(preferencelist=("plain",))
    html_part = msg.get_body(preferencelist=("html",))
    text = text_part.get_content() if text_part else ""
    html = _clean(html_part.get_content()) if html_part else ""
    if not text and html:
        text = re.sub(r"<[^>]+>", " ", html)
    attachments = any(True for _ in msg.iter_attachments())
    return MailMessage(
        direction="in", uid=uid, from_name=name[:200], from_addr=addr[:254],
        to_addrs=str(msg.get("To", ""))[:1000], subject=str(msg.get("Subject", ""))[:500],
        body_text=text[:MAX_BODY], body_html=html, has_attachments=attachments, sent_at=when)


def sync_inbox():
    """Fetch mails newer than the last stored UID. Returns the number of new messages."""
    state = MailSync.load()
    if not configured():
        raise MailError("رمز صندوق ایمیل تنظیم نشده است (متغیر MAIL_PASSWORD).")
    last = (MailMessage.objects.filter(direction="in", uid__isnull=False)
            .order_by("-uid").values_list("uid", flat=True).first() or 0)
    new = 0
    try:
        box = imaplib.IMAP4_SSL(settings.MAIL_IMAP_HOST, settings.MAIL_IMAP_PORT, timeout=20)
        try:
            box.login(settings.MAIL_USER, settings.MAIL_PASSWORD)
            box.select("INBOX", readonly=True)
            typ, data = box.uid("SEARCH", None, f"UID {last + 1}:*")
            uids = [int(u) for u in (data[0] or b"").split() if int(u) > last]
            if not last:
                uids = uids[-FIRST_SYNC_LIMIT:]
            for uid in uids:
                typ, parts = box.uid("FETCH", str(uid), "(BODY.PEEK[])")
                raw = next((p[1] for p in parts if isinstance(p, tuple)), None)
                if raw:
                    _save(_parse(raw, uid))
                    new += 1
        finally:
            try:
                box.logout()
            except Exception:
                pass
    except (imaplib.IMAP4.error, OSError) as exc:
        state.last_error = f"{type(exc).__name__}: {exc}"[:300]
        state.save()
        raise MailError("اتصال به سرور ایمیل ناموفق بود. تنظیمات و رمز را بررسی کنید.") from exc
    state.last_sync, state.last_error = timezone.now(), ""
    state.save()
    return new


def _save(obj):
    if not MailMessage.objects.filter(direction="in", uid=obj.uid).exists():
        obj.save()


def stale(minutes=5):
    s = MailSync.load()
    return not s.last_sync or (timezone.now() - s.last_sync).total_seconds() > minutes * 60


def send(to, subject, body, cc="", reply_to_msg=None):
    """Send via SMTP and keep a copy in the 'sent' list."""
    if not configured():
        raise MailError("رمز صندوق ایمیل تنظیم نشده است (متغیر MAIL_PASSWORD).")
    to_list = [a.strip() for a in re.split(r"[,;\s]+", to) if a.strip()]
    cc_list = [a.strip() for a in re.split(r"[,;\s]+", cc) if a.strip()]
    mail = EmailMessage(subject=subject, body=body, to=to_list, cc=cc_list)
    error = ""
    try:
        mail.send(fail_silently=False)
    except Exception as exc:  # smtplib.* / OSError
        log.warning("mail send failed: %s", exc)
        error = f"{type(exc).__name__}: {exc}"[:300]
    MailMessage.objects.create(
        direction="out", from_name=settings.MAIL_FROM_NAME, from_addr=settings.MAIL_USER,
        to_addrs=", ".join(to_list), subject=subject[:500], body_text=body, sent_at=timezone.now(),
        is_read=True, error=error)
    if error:
        raise MailError("ارسال ایمیل ناموفق بود. تنظیمات SMTP و رمز را بررسی کنید.")
