from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})

@register.filter
def dict_get(d, key):
    return d.get(key)

@register.filter
def join_ids(schedules):
    return ','.join(str(s.id) for s in schedules)

@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, None)