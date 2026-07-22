from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return None
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None

@register.filter
def replace(value, arg):
    if not isinstance(value, str):
        return value
    return value.replace(arg, ' ')
