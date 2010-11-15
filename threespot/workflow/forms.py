from django import forms

from app_settings import UNPUBLISHED_STATES, PUBLISHED_STATE

class WorkflowAdminFormMixin(forms.ModelForm):
    
    def clean(self):
        """
        Make sure that an item that is a draft copy is always unpublished.
        """
        cleaned_data = super(WorkflowAdminFormMixin, self).clean()
        status = cleaned_data.get('status')
        copy_of = self.instance.copy_of
        if status == PUBLISHED_STATE and copy_of:
            model_name = self.instance._meta.verbose_name
            raise forms.ValidationError((
                "This %s is a copy of a draft %s that is already "
                "published. If you want to publish this over top of the " 
                "existing item, you can do so by merging it."
            ) % (model_name, model_name))
        return cleaned_data