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

# Any additional kwargs for the status field. By default, the field
# should be indexed for obvious performance reasons.
ADDITIONAL_STATUS_KWARGS = workflow_settings_mgr.create(
    'ADDITIONAL_STATUS_KWARGS',
    default = {'db_index': True}
)

# Subclass the Workflow model from django-reversion.
USE_DJANGO_REVERSION = workflow_settings_mgr.create('USE_DJANGO_REVERSION',
    default = False
)

# If True, will consider content dated in the future "unpublished" regardless of
# the status. Will use the model's Meta 'get-latest-by' field to determine which
# model field is to be used for the date.
ENABLE_POSTDATED_PUBLISHING = workflow_settings_mgr.create(
    'ENABLE_POSTDATED_PUBLISHING',
    default=True
)
