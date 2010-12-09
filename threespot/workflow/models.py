from django.db import models
from django.utils.translation import ugettext_lazy as _

from app_settings import WORKFLOW_CHOICES, PUBLISHED_STATE, \
    UNPUBLISHED_STATES, DEFAULT_STATE, ADDITIONAL_STATUS_KWARGS
from managers import WorkflowManager


status_kwargs = {
    'choices': WORKFLOW_CHOICES,
    'max_length': 1
}
if DEFAULT_STATE:
    status_kwargs['default'] = DEFAULT_STATE
if ADDITIONAL_STATUS_KWARGS:
    status_kwargs.update(ADDITIONAL_STATUS_KWARGS)

class WorkflowMixin(models.Model):
    """
    An abstract model mixin that can be used provide a publication status.
    """
    status = models.CharField(_("Status"), **status_kwargs)
    copy_of = models.OneToOneField('self', null=True)
    objects = WorkflowManager()
    
    class Meta:
        abstract = True
    
    def is_draft_copy(self):
        """ Is this item a draft copy?"""
        return bool(self.copy_of)
    is_draft_copy.boolean = True
    
    def get_draft_copy(self):
        """
        Retrieve the draft copy of this item if it exists.
        """
        return self._default_manager.filter(copy_of__id=self.id)
    
    def is_published(self):
        """ Boolean property indicating if item is published."""
        return self.status == PUBLISHED_STATE
    is_published.boolean = True
    
    def publish(self):
        """Convenience method to publish a post"""
        if self.status != PUBLISHED_STATE:
            self.status = PUBLISHED_STATE
            self.save()
            return True
    
    def unpublish(self, status=UNPUBLISHED_STATES[0][0]):
        """Convenience method to unpublish a post"""        
        if self.status != status:
            self.status = status
            self.save()
            return True