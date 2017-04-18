from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def jwt_token(context):
    request = context['request']
    return request.session.get('jwt_token', '')
