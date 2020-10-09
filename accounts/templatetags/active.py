from django import template
from django.shortcuts import reverse

register = template.Library()

@register.simple_tag
def add_active(request, name, slug):
    path = reverse(name, kwargs={'slug': slug}) if slug else reverse(name)

    if request.path == path:
        return "active"

    return ""

@register.filter(name='add_css')
def add_css(field, css):
    """Removes all values or args from the given string"""
    return field.as_widget(attrs={"class": css})