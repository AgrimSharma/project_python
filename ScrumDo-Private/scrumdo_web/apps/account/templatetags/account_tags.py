from django import template
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.template import Library, loader, Context
from apps.avatar.templatetags.avatar_tags import avatar_url
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def realname(value):
    """ Example usage with user object:
    {{ user|realname }}
    """
    try:
        if value.first_name or value.last_name:
            return ("%s %s" % (value.first_name, value.last_name)).strip()
        else: return value.username
    except AttributeError: return value
realname.is_safe = True

@register.filter(is_safe=True, needs_autoescape=False)
def hover_username(value):
    name = realname(value)
    return mark_safe("<span class=\"user-hover\" data-user-id=\"%d\">%s</span>" % (value.id,name))

