"""Layered, dependency-free anti-spam for public forms (contact + job applications).

No third-party service is used (works inside Iran, no tracking):
 1. honeypot field (checked by the forms)
 2. signed one-time challenge: a tiny arithmetic question + timestamp; too fast / too old / replayed => rejected
 3. per-IP rate limit shared by all gunicorn workers (file cache)
 4. content rules: too many links is rejected
"""
import re
import secrets
import time

from django.conf import settings
from django.core import signing
from django.core.cache import cache

SALT = "zhasco.antispam.v1"
_FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
URL_RE = re.compile(r"(https?://|www\.|\[url|<a\s)", re.I)


def min_seconds():
    return getattr(settings, "ANTISPAM_MIN_SECONDS", 4)


def max_seconds():
    return getattr(settings, "ANTISPAM_MAX_SECONDS", 2 * 3600)


def new_challenge():
    """Returns {'token': signed string, 'question': '۳ + ۷'} to render in the form."""
    a, b = secrets.randbelow(8) + 2, secrets.randbelow(8) + 2
    token = signing.dumps({"a": a, "b": b, "t": int(time.time()), "n": secrets.token_hex(8)}, salt=SALT)
    return {"token": token, "question": f"{a} + {b}".translate(_FA)}


def client_ip(request):
    """Client address behind the Coolify/Traefik proxy: the last X-Forwarded-For entry is the one the proxy added."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    parts = [p.strip() for p in xff.split(",") if p.strip()]
    return (parts[-1] if parts else request.META.get("REMOTE_ADDR", "")) or "unknown"


def hit(scope, ident, limit, window):
    """Count an attempt; returns False when `limit` per `window` seconds is exceeded."""
    key = f"rl:{scope}:{ident}"
    if cache.add(key, 1, window):
        return True
    try:
        return cache.incr(key) <= limit
    except ValueError:
        cache.set(key, 1, window)
        return True


def check_rate(request, scope, limit=5, window=3600):
    return hit(scope, client_ip(request), limit, window)


def verify(token, answer):
    """Returns None when the challenge is valid, otherwise a Persian error message. One-time use."""
    if not token or answer is None:
        return "پاسخ سؤال امنیتی را وارد کنید."
    try:
        data = signing.loads(token, salt=SALT, max_age=max_seconds())
    except signing.SignatureExpired:
        return "زمان فرم به پایان رسید؛ لطفاً پاسخ را دوباره وارد کنید."
    except signing.BadSignature:
        return "فرم نامعتبر است؛ صفحه را دوباره باز کنید."
    age = time.time() - data["t"]
    try:
        value = int(str(answer).strip().translate(_FA_DIGITS))
    except ValueError:
        return "پاسخ سؤال امنیتی باید یک عدد باشد."
    if value != data["a"] + data["b"]:
        return "پاسخ سؤال امنیتی درست نیست."
    if age < min_seconds():
        return "فرم خیلی سریع ارسال شد؛ لطفاً چند ثانیه صبر کنید و دوباره بفرستید."
    if not cache.add(f"used:{data['n']}", 1, max_seconds()):
        return "این فرم قبلاً ارسال شده است؛ صفحه را دوباره باز کنید."
    return None


def too_many_links(*texts, limit=1):
    return sum(len(URL_RE.findall(t or "")) for t in texts) > limit


def check_submission(request, scope, *texts, limit=5, window=3600):
    """Run all non-field checks. Returns a Persian error message or None."""
    if not check_rate(request, scope, limit, window):
        return "تعداد ارسال‌ها از این دستگاه زیاد بوده است؛ لطفاً بعداً دوباره تلاش کنید."
    err = verify(request.POST.get("ts_token"), request.POST.get("captcha"))
    if err:
        return err
    if too_many_links(*texts):
        return "پیام شما شامل لینک‌های متعدد است و ثبت نشد. لطفاً فقط یک لینک بگذارید یا آن را حذف کنید."
    return None
