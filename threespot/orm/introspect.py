from django.db import models

from threespot.functional import partial

def get_referencing_models(my_model, field_instance=None):
    """
    This function returns a list of all models which have some sort of relation 
    to the given ``my_model`` model. You can restrict the types of relations by 
    passing a related field (e.g. ``models.ManyToManyField``) to the 
    ``field_instance`` argument. Only models which are related to your model in 
    that particular way will be returned.
    
    Note: This function does not take Generic relations into account.
    """
    model_list = []
    for model in models.get_models():
        for field in model._meta.fields:
            if field_instance:
                if isinstance(field, field_instance):
                    if field.rel.to == my_model:
                        model_list.append(model)
                        continue
            else:
                if field.rel.to == my_model:
                    model_list.append(model)
                    continue
    return model_list 

# A shortcut function to return all models that have a 
# OneToOneField referencing your model.
get_referencing_o2o_models = partial(
    get_referencing_models,
    field_instance=models.OneToOneField
)

# A shortcut function to return all models that have a 
# ManyToManyField referencing your model.
get_referencing_m2m_models = partial(
    get_referencing_models,
    field_instance=models.ManyToManyField
)

# A shortcut function to return all models that have a 
# ForeignKey referencing your model.
get_referencing_fk_models = partial(
    get_referencing_models,
    field_instance=models.ForeignKey
)