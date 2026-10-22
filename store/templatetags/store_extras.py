from django import template

register = template.Library()


@register.filter
def money(value):
    """50.00 -> '50', 41.2 -> '41.20'."""
    text = f"{value:.2f}"
    return text[:-3] if text.endswith(".00") else text
