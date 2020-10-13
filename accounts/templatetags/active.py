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

@register.filter(name='add_id')
def add_id(field, id):
    """Removes all values or args from the given string"""
    return field.as_widget(attrs={"id": field.id_for_label + '-' + id})

@register.filter(name='add_id_css')
def add_id_css(field, id_class):
    """Removes all values or args from the given string"""
    id_class = id_class.split(',')
    return field.as_widget(attrs={"id": field.id_for_label + '-' + id_class[0], 'class': id_class[1]})