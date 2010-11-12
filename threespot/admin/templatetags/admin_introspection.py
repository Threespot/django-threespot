from django import template
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models

register = template.Library()

def verify_model_instance(f):
    """
    Utility function to verify that the first argument is a model instance.
    """
    def _inner(value):
        if not isinstance(value, models.Model):
            return ''
        else:
            return f(value)
    return _inner

@verify_model_instance
def app_label(value):
    """ Template tag that returns the name of the app an item belongs too"""
    return value._meta.app_label

@verify_model_instance
def model_verbose_name(value):
    """ Template tag that returns the verbose name of an item."""
    return value._meta.verbose_name

@verify_model_instance
def edit_object_url(value):
    """Template tag that gets the url to edit an item in the admin."""
    args = (value._meta.app_label, value._meta.module_name)
    try:
        return reverse('admin:%s_%s_change' % args,  args=[value.id])
    except NoReverseMatch:
        return ''

register.filter('app_label', app_label)
register.filter('model_verbose_name', model_verbose_name)
register.filter('edit_object_url', edit_object_url)
