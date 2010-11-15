from django.db import models

from app_settings import PUBLISHED_STATE

class WorkflowManager(models.Manager): 
    """
    A manager used to fetch published objects.
    """
    
    def published(self):
        """ Returns a set of published items only."""
        return super(WorkflowManager, self).get_query_set().filter(
            status=PUBLISHED_STATE
        )