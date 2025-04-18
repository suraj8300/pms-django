from django import template
from django.utils import timezone
import datetime

register = template.Library()

@register.filter
def days_left(expiration_date):
    if not expiration_date or not isinstance(expiration_date, datetime.date):
        return None
    current_date = timezone.now().date()
    delta = expiration_date - current_date
    return max(0, delta.days)  # Returns days left, or 0 if expired