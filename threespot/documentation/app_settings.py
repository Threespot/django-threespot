from os import path
from django.conf import settings
from django.utils.importlib import import_module

from threespot.configure import SettingsManager

documentation_settings_mgr = SettingsManager("DOCUMENTATION")

PUBLISH_PATH = documentation_settings_mgr.create('PUBLISH_PATH', 
    default=path.join(settings.MEDIA_ROOT, 'docs')
)

def _get_default_docs_path():
    """
    Find the path to the root folder of the project.
    
    We assume the ROOT_URLCONF is in the project root, so it is imported 
    and the path derived from that.
    """
    urlconf_path = import_module(settings.ROOT_URLCONF).__file__
    project_dir = path.abspath(path.dirname(urlconf_path))
    return path.join(project_dir, 'docs')

SOURCE_LOCATION = documentation_settings_mgr.create('SOURCE_LOCATION',
    default=_get_default_docs_path()
)