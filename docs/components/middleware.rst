===================
Middleware 
===================

Maintenance
------------------------------------------------------------------

The ``threespot.middleware.maintenance.MaintenanceModeMiddleware`` middleware is used to put your site in "Maintenance Mode," in other words to temporary shutdown your site and display a maintenance page for all users. In this mode *all* requests are intercepted and a specific maintenance mode view is returned instead. This view looks for a ``503.html`` template in the root of the templates directory. The 503 status code is used for the view to prevent the maintenance message from being indexed by crawlers. This ``503.html`` template has the the following context variables:

* ``MEDIA_URL``
* ``uptoday``: True/False depending on whether the site is expected to be back up on the current day.
* ``uptime``: The time that the site is expected to be back up (equal to ``EXPECTED_UPTIME`` if set).
    
Available settings
-------------------

EXPECTED_UPTIME
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Default: ``None``

Note this must be a datetime object if set. If not set, ``uptoday`` 
and ``uptime`` are None in the template context. This should be a datetime object specifying when the site will be back up (if this is known).