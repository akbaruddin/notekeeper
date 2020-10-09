from django import template

register = template.Library()

@register.filter(name='add_css')
def add_css(field, css):
    """Removes all values or args from the given string"""
    return field.as_widget(attrs={"class": css})


