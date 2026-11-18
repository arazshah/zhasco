import jdatetime
import nh3
from django import template
from django.utils import timezone
from django.utils.safestring import mark_safe

register = template.Library()

_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
          "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
ALLOWED_TAGS = {"p", "br", "strong", "b", "em", "i", "u", "ul", "ol", "li", "h2", "h3", "h4", "blockquote",
                "a", "img", "figure", "figcaption", "table", "thead", "tbody", "tr", "th", "td", "div", "span"}
ALLOWED_ATTRS = {"a": {"href", "title", "target"}, "img": {"src", "alt", "width", "height"}, "*": {"dir", "class"}}


@register.filter
def fa(value):
    """Latin digits -> Persian digits."""
    if value is None:
        return ""
    return str(value).translate(_FA)


@register.filter
def fa_num(value):
    """Integer with thousands separator, Persian digits."""
    try:
        return f"{int(value):,}".replace(",", "٬").translate(_FA)
    except (TypeError, ValueError):
        return fa(value)


@register.filter
def jdate(value, fmt="long"):
    if not value:
        return ""
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    jd = jdatetime.datetime.fromgregorian(datetime=value)
    if fmt == "short":
        return fa(f"{jd.year}/{jd.month:02d}/{jd.day:02d}")
    return fa(f"{jd.day} {MONTHS[jd.month - 1]} {jd.year}")


@register.filter
def clean_html(value):
    """Sanitise admin-authored rich text; plain text gets paragraphs."""
    if not value:
        return ""
    text = str(value)
    if "<" not in text:
        paras = [p.strip() for p in text.replace("\r", "").split("\n\n") if p.strip()]
        text = "".join(f"<p>{nh3.clean(p, tags=set()).replace(chr(10), '<br>')}</p>" for p in paras)
    return mark_safe(nh3.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS,
                               link_rel="noopener noreferrer", url_schemes={"http", "https", "mailto", "tel"}))


@register.filter
def lines(value):
    return [ln.strip() for ln in str(value or "").splitlines() if ln.strip()]


@register.filter
def level(count):
    """Colour level of a province on the map by project count."""
    n = int(count or 0)
    return 0 if n <= 0 else 1 if n < 5 else 2 if n < 15 else 3 if n < 40 else 4
