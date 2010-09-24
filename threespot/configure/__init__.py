from os import path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

"""
Utilities for working with Django settings.
"""

def get_folder_path(module_location, dirname):
    """ Return the full path to the ``dirname`` in module directory."""
    here = path.dirname(module_location)
    return path.normpath(path.join(here, dirname))

class SettingsManager(object):
    """
    SettingsManager helps you manage settings for your Django application and 
    making them overrideable in the main project settings file. 
    
    Here's an example, creating settings for an app named `foo`. When you
    create a new instance of the manager, you can (optionally) include a 
    namespace:
    
    >>> foo_settings_mgr = SettingsManager("FOO")
    
    ... and then define various settings for your app:
    
    >>> WORKFLOW_CHOICES = foo_settings_mgr.create('WORKFLOW_CHOICES',
    ...     default=(('d', 'Draft'), ('p', 'Published'),)
    ... )
    >>> VIEW_TTL = foo_settings_mgr.create('VIEW_TTL', required=True)
    
    
    Either of these settings can be overridden with a setting called 
    `FOO_WORKFLOW_CHOICES` and `FOO_VIEW_TTL` in the project settings 
    file (note the addition of the namespace to each setting; it's good practice 
    to make the namespace the same name as your app). In the first example, the 
    `default` argument sets the default setting. In the second example, the 
    `required` argument will cause the manager to raise an 
    `ImproperlyConfigured` exception if `FOO_VIEW_TTL` is *not* set in the main 
    settings file. 
    """
    
    registry = {}
    
    def __init__(self, namespace=''):
        self.namespace = namespace and namespace.upper() + '_' or ''

    def create(self, setting_name, default=None, required=False):
        """
        Creates a new setting for your application. The `default` argument is 
        the value you want your application to have. The `required` causes the 
        manager to raise an `ImproperlyConfigured` exception if the setting is 
        not set in the django project's settings file.
        """
        setting_name = "%s_%s" % (self.namespace, setting_name)
        if required and not default:
            if not hasattr(settings, settings_name):
                raise ImproperlyConfigured, (
                "%s must be set to use this django application."         
                ) % setting_name
        self.registry[setting_name] = getattr(settings, setting_name, default)
        return self.registry[setting_name]
