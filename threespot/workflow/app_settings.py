from threespot.configure import SettingsManager

workflow_settings_mgr = SettingsManager("WORKFLOW")

# The publication status types a document can have
WORKFLOW_CHOICES = workflow_settings_mgr.create('WORKFLOW_CHOICES',
    default=(
        ('d', 'Draft'), 
        ('p', 'Published'),
    )
)

# The publication status that means a document is published
PUBLISHED_STATE = workflow_settings_mgr.create('WORKFLOW_CHOICES',
    default='p'
)

UNPUBLISHED_STATES = filter(
    lambda c: c[0] != PUBLISHED_STATE, 
    WORKFLOW_CHOICES
)

# Subclass the Workflow model from django-reversion.
USE_DJANGO_REVERSION = False