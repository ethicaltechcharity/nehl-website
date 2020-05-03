from django import template

register = template.Library()


@register.inclusion_tag('fragments/pagination.html')
def paginate(pagination_object):
    return {'pagination_object': pagination_object}
