from django.db import models

from app_settings import PUBLISHED_STATE

class WorkflowManager(models.Manager): 
    """
    A manager used to fetch published objects.
    """
    
    @staticmethod
    def _extract_select_related_args(select_related):
        """
        Parses possible ``select_related`` arguments into a set
        of useable args and kwargs for Django's ``select_related``
        queryset. If ``True``, ``select_related`` will be called with
        no arguments, if a tuple, those will be assumed to be the
        exact FK fields to follow, if an integer, ``depth=N`` will
        be passed.
        """
        if select_related is True:
            args, kwargs = [], {}
        elif type(select_related) == tuple:
            args, kwargs = select_related, {}
        elif type(select_related) == int:
            args, kwargs = [], {'depth': int}
        else:
            raise TypeError((
                "The argument passed to _extract_select_related_args needs to "
                "be a boolean, tuple, or string. You passed an argument of "
                "the type %r."
            ) % type(select_related))
        return args, kwargs
    
    def get_query_set(self, select_related=None):
        """
        Patches ``select_related`` into the standard get_query_set method on
        a model manager.
        """
        query_set = super(WorkflowManager, self).get_query_set()
        if select_related:
            args, kwargs = self._extract_select_related_args(select_related)
            return query_set.select_related(*args, **kwargs)
        return query_set

    def published(self, select_related=None):
        """ Returns all published items."""
        return self.get_query_set(select_related=select_related).filter(
            status=PUBLISHED_STATE
        )
    
    def unpublished(self, select_related=None):
        """ Returns all unpublished objects."""
        return self.get_query_set(select_related=select_related).exclude(
            status=PUBLISHED_STATE
        )        
    
    def draft_copies(self, select_related=None):
        """ Returns all draft copies."""
        return self.get_query_set(select_related=select_related).exclude(
            copy_of__exact=None
        )