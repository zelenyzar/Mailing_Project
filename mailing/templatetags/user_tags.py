from django import template
from mailing.mixins import is_manager as check_is_manager

register = template.Library()

@register.simple_tag
def get_user_email(user):
    return user.email if user else "Гость"

@register.filter
def is_manager(user):
    return user.is_staff