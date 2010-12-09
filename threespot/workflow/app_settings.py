from threespot.configure import SettingsManager

workflow_settings_mgr = SettingsManager(namespace="WORKFLOW")

# The publication status types a document can have
WORKFLOW_CHOICES = workflow_settings_mgr.create('WORKFLOW_CHOICES',
    default=(
        ('d', 'Draft'), 
        ('p', 'Published'),
    )
)

# The publication status that means a document is published
PUBLISHED_STATE = workflow_settings_mgr.create('PUBLISHED_STATE',
    default='p'
)

UNPUBLISHED_STATES = filter(
    lambda c: c[0] != PUBLISHED_STATE, 
    WORKFLOW_CHOICES
)

# The default status (if none, set to None)
DEFAULT_STATE = workflow_settings_mgr.create('DEFAULT_STATE',
    default = UNPUBLISHED_STATES[0]
)

# Any additional kwargs for the status field
ADDITIONAL_STATUS_KWARGS = workflow_settings_mgr.create(
    'ADDITIONAL_STATUS_KWARGS',
    default = {}
)

# Subclass the Workflow model from django-reversion.
USE_DJANGO_REVERSION = workflow_settings_mgr.create('USE_DJANGO_REVERSION',
    default = False
)

