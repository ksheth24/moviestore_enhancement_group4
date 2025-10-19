from django import template

register = template.Library()

@register.filter
def cents_to_dollars(value):
    """Convert cents to dollars"""
    try:
        return float(value) / 100
    except (ValueError, TypeError):
        return 0.0
