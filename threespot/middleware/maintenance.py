from datetime import datetime
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render_to_response

class MaintenanceModeMiddleware:
    """
    This middleware is used to put your site in "Maintenance Mode".
    
    It intercepts all requests and returns a view that is rendered with a 
    503.html template in the root of the templates directory. This template has
    the usual RequestContext variables and two others: 
    
        uptoday: True/False depending on whether the site is expected to be back
        up in the current day.
        
        uptime: The time that the site is expected to be back up.
        
    Both of these variables are controlled by an ``EXPECTED_UPTIME`` setting in 
    settings.py. Note this must be a datetime object. If not set, ``uptoday`` 
    and ``uptime`` are None in the template context. 
    
    The 503 status code is used to prevent the maintenance message from being 
    indexed by crawlers.
    
    """
    
    def process_request(self, request):
        if hasattr(settings, 'EXPECTED_UPTIME'):
            uptime = settings.EXPECTED_UPTIME
            if not isinstance(uptime, datetime):
                raise ImproperlyConfigured, (
                    "EXPECTED_UPTIME must be a datetime object."
                )
            diff = uptime - datetime.now()
            uptoday = diff.days == 0
            # If delta is negative, we've already passed the expected 
            # uptime, so we'll set the uptime to None.
            if abs(diff) != diff:
                uptime = None
                uptoday = None
        else:
            uptime = None
            uptoday = None
        response = render_to_response("503.html", {
            'MEDIA_URL': settings.MEDIA_URL,
            'uptoday': uptoday,
            'uptime': uptime
        })
        # 503 Means "Service Unavailable". W3C description:
        # "The server is currently unable to handle the request due to a 
        # temporary overloading or maintenance of the server."
        response.status_code = 503
        return response