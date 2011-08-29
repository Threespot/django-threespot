from django.contrib.admin.views.decorators import staff_member_required
from django.views.static import serve 

from threespot.documentation.app_settings import PUBLISH_PATH

@staff_member_required
def documentation(*args, **kwargs):
    """
    Uses the ugly, but good-enough django static files server. Ensures the
    server serves from the ``DOCUMENTATION_PUBLISH_PATH`` setting, and
    that only staff members can see it.
    """
    kwargs['document_root'] = PUBLISH_PATH
    kwargs['show_indexes'] = False
    return serve(*args, **kwargs)