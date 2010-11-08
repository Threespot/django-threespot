==========================================
Django Configuration and Settings Helpers
==========================================

The SettingsManager
---------------------

``SettingsManager`` helps you manage settings for your Django application and 
making them overrideable in the main project settings file. 

Here's an example, creating settings for an app named `foo`. When you
create a new instance of the manager, you can (optionally) include a 
namespace::

    from threespot.configure import SettingsManager
    
    foo_settings_mgr = SettingsManager("FOO")

...and then define various settings for your app::

    WORKFLOW_CHOICES = foo_settings_mgr.create('WORKFLOW_CHOICES',      
        default=(('d', 'Draft'), ('p', 'Published'),)
    )
    VIEW_TTL = foo_settings_mgr.create('VIEW_TTL', required=True)

Either of these settings can be overridden with a setting called 
``FOO_WORKFLOW_CHOICES`` and ``FOO_VIEW_TTL`` in the project settings 
file (note the addition of the namespace to each setting; it's good practice 
to make the namespace the same name as your app). In the first example, the 
``default`` argument sets the default setting. In the second example, the 
``required`` argument will cause the manager to raise an 
``ImproperlyConfigured`` exception if ``FOO_VIEW_TTL`` is *not* set in the main 
settings file.

You can then use these settings in any module in your application::

    from myapp import app_settings
    
    @cache_page(app_settings.VIEW_TTL)
    def myview(reauest):
        return HttpResponse("Hello, world.")