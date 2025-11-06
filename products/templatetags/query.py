from urllib.parse import urlencode
from django import template

register = template.Library()

@register.simple_tag
def build_query_string(request, **kwargs):
    query_dict = request.GET.copy()
    query_dict.update(kwargs)
    return urlencode(query_dict)