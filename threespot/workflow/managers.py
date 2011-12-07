from datetime import datetime

from django.db import models

from app_settings import ENABLE_POSTDATED_PUBLISHING, PUBLISHED_STATE


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

    def _get_postdate_field(self):
        """
        Return the name of the model meta ``get_latest_by`` field, or
        None if the field is unset or ``ENABLE_POSTDATED_PUBLISHING`` is off.
        """
        if not ENABLE_POSTDATED_PUBLISHING:
            return None
        return self.model._meta.get_latest_by
    
    def get_postdate_publish_filter_kwarg(self):
        """
        Return the name of the filter argument to filter a queryset by 
        non-future dates if it's available and ``ENABLE_POSTDATED_PUBLISHING`` 
        is on.
        """
        field_name = self._get_postdate_field()
        if field_name:
            return field_name + "__lte"
        return None

    def get_postdate_unpublish_filter_kwarg(self):
        """
        Return the name of the filter argument to filter a queryset by 
        future dates if it's available and ``ENABLE_POSTDATED_PUBLISHING`` 
        is on.
        """
        field_name = self._get_postdate_field()
        if field_name:
            return field_name + "__gt"
        return None

    def _get_expanded_queryset(self, select_related=None):
        # Patches ``select_related`` into the standard get_query_set method on
        # a model manager.
        if select_related:
            args, kwargs = self._extract_select_related_args(select_related)
            qs = self.get_query_set().select_related(*args, **kwargs)
        else:
            qs = self.get_query_set()
        return qs
    
    def published(self, select_related=None):
        """ Returns all published items."""
        qs = self._get_expanded_queryset(select_related=select_related)
        filter_kwargs = {'status': PUBLISHED_STATE}
        postdate_kwarg = self.get_postdate_publish_filter_kwarg()
        if postdate_kwarg:
            filter_kwargs[postdate_kwarg] = datetime.now()
        return qs.filter(**filter_kwargs)
    
    def unpublished(self, select_related=None):
        """ Returns all unpublished objects."""
        qs = self._get_expanded_queryset(select_related=select_related)
        postdate_kw = self.get_postdate_unpublish_filter_kwarg()
        if postdate_kw:
            return qs.filter(
                ~models.Q(status=PUBLISHED_STATE) | models.Q(**{postdate_kw: datetime.now()})
            )
        return qs.exclude(status=PUBLISHED_STATE)        
    
    def draft_copies(self, select_related=None):
        """ Returns all draft copies."""
        qs = self._get_expanded_queryset(select_related=select_related)
        return qs.exclude(copy_of__exact=None)