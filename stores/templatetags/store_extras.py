# stores/templatetags/store_extras.py

from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def format_timedelta(td):
    """
    Formats a timedelta object into a human-readable string.
    Example: "2 hours, 30 minutes remaining"
    """
    if not isinstance(td, timedelta):
        return td  # Return as-is if not a timedelta

    total_seconds = int(td.total_seconds())
    if total_seconds <= 0:
        return "Expired"

    periods = [
        ('year', 60*60*24*365),
        ('month', 60*60*24*30),
        ('day', 60*60*24),
        ('hour', 60*60),
        ('minute', 60),
        ('second', 1),
    ]

    strings = []
    for period_name, period_seconds in periods:
        if total_seconds >= period_seconds:
            period_value, total_seconds = divmod(total_seconds, period_seconds)
            if period_value > 0:
                strings.append(f"{period_value} {period_name}{'s' if period_value != 1 else ''}")

    return ', '.join(strings)
