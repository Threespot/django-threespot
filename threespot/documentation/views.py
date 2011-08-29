import re

from django.contrib.admin.views.decorators import staff_member_required
from django.views.static import serve 

from threespot.documentation.app_settings import PUBLISH_PATH


_web_file = re.compile("\.css|js|html|png|gif|jpg|jpeg|ico{1}$")

@staff_member_required
def documentation(request, path, *args, **kwargs):
    """
    Uses the ugly, but good-enough django static files server. Ensures the
    server serves from the ``DOCUMENTATION_PUBLISH_PATH`` setting, and
    that only staff members can see it.
    """
    kwargs['document_root'] = PUBLISH_PATH
    kwargs['show_indexes'] = False
    if not _web_file.search(path):
        path += "index.html"
    print path
    return serve(request, path, *args, **kwargs)