from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary
    Usage: {{ mydict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter(name='get_field')
def get_field(form, field_name):
    """
    Template filter to get a form field by name.
    Usage: {{ form|get_field:'field_name' }}
    """
    if form is None or not hasattr(form, 'fields'):
        return None
    return form[field_name] if field_name in form.fields else None


@register.filter(name='getattr')
def getattr_filter(obj, attr_name):
    """
    Template filter to get an attribute from an object.
    Usage: {{ obj|getattr:'attribute_name' }}
    """
    if obj is None:
        return None
    return getattr(obj, attr_name, None)
