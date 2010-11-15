from django.db import models

from app_settings import PUBLISHED_STATE

class WorkflowManager(models.Manager): 
    """
    A manager used to fetch published objects.
    """
    
    def published(self):
        """ Returns all published items."""
        return super(WorkflowManager, self).get_query_set().filter(
            status=PUBLISHED_STATE
        )
    
    def unpublished(self):
        """ Returns all unpublished objects."""
        return super(WorkflowManager, self).get_query_set().exclude(
            status=PUBLISHED_STATE
        )        
    
    def draft_copies(self):
        """ Returns all draft copies."""
        return super(WorkflowManager, self).get_query_set().exclude(
            copy_of__exact=None
        )
