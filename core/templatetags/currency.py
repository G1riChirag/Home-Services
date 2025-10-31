# core/templatetags/currency.py
from django import template

register = template.Library()

@register.filter
def cents_to_dollars(value):
    """
    Convert an integer amount in cents to a human USD/AUD-style string.
    19900 -> "199"
    1299  -> "12.99"
    """
    try:
        cents = int(value)
    except (TypeError, ValueError):
        return "0"
    dollars = cents / 100.0
    s = f"{dollars:.2f}"
    # strip trailing .00 or .0
    if s.endswith("00"):
        s = s[:-3]
    elif s.endswith("0"):
        s = s[:-1]
    return s
