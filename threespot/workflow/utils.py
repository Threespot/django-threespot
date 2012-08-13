from datetime import datetime

from django.conf import settings


def get_current_datetime():
    """
    A shim function to provide a TZ-aware "now" datetime object
    in Django >= 1.4 if the ``USE_TZ`` sett8ing is True, and a standard
    datetime "now" object otherwise.
    """
    if hasattr(settings, 'USE_TZ') and settings.USE_TZ:
        from django.utils import timezone
        return timezone.now()
    else:
        return datetime.now()