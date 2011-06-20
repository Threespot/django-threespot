from django.contrib.contenttypes import generic
from django.db import models

from threespot.functional import partial

"""
This module provides helper functions for finding our more information about a specific model or object.
"""

def get_referencing_models(my_model, field_instance=None):
    """
    This function returns a list of all models which have some sort of relation 
    to the given ``my_model`` model. You can restrict the types of relations by 
    passing a related field (e.g. ``models.ManyToManyField``) to the 
    ``field_instance`` argument. Only models which are related to your model in 
    that particular way will be returned.
    
    Note: This function does not take Generic relations into account.
    
    This function returns a dictionary:
    
        {
            'model': <The referencing model>,
            'field_names': [<List of field names referencing the given model>]
            'm2m_field_names': [<List of referencing M2M field names>]

        }
    
    """
    model_data_list = []
    for model in models.get_models():
        model_data = {
            'model': model,
            'field_names': [],
            'm2m_field_names': []
        }
        if not (field_instance == models.ManyToManyField):
            for field in model._meta.fields:
                if not field_instance or isinstance(field, field_instance):
                    if field.rel and field.rel.to == my_model:
                        model_data['field_names'].append(field.name)
        if not field_instance or field_instance == models.ManyToManyField:
            for field in model._meta.many_to_many:
                if field.rel and field.rel.to == my_model:
                    model_data['m2m_field_names'].append(field.name)
        if len(model_data['field_names']) > 0 \
            or len(model_data['m2m_field_names']) > 0:
            model_data_list.append(model_data)
    return model_data_list 

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

_default_queryset = lambda model: model.objects.all()


def get_generic_referencing_objects(my_object, 
                                    get_queryset=_default_queryset):
    """
    This function returns a list of all objects which have some sort of generic 
    relationship to the given ``my_object`` object. One optional argument:
    
        :get_queryset: A function which returns a queryset of related model 
         objects. By default, Model.objects.all() is used.
    
    """
    object_list = []
    my_model = my_object.__class__
    # Any model which has virtual fields could have Generic FK references to
    # the given model.
    for model in (m for m in models.get_models() \
        if len(m._meta.virtual_fields) > 0):
        virtual_field_properties = []
        for field in model._meta.virtual_fields:
            virtual_field_properties.append(
                (field.ct_field, field.fk_field,)
            )
        for obj in get_queryset(model):
            for ct_field, fk_field in virtual_field_properties:
                ct = getattr(obj, ct_field)
                fk = getattr(obj, fk_field)
                if ct.model_class() == my_model and fk == my_object.pk:
                    object_list.append(obj)
                    continue
    return object_list

def get_referencing_objects(my_object, get_queryset=_default_queryset):
    """
    This function returns a list of all objects which have some sort of 
    relationship to the given ``my_object`` object. One optional argument:
    
        :get_queryset: A function which returns a queryset of the related model
         objects. By default, Model.objects.all() is used.
    
    """
    my_model = my_object.__class__
    referencing_objects = []
    for model_data in get_referencing_models(my_model):
        for field_name in model_data['field_names']:
            for obj in get_queryset(model_data['model']):
                if getattr(obj, field_name).pk == my_object.pk:
                    referencing_objects.append(obj)
        for field in model_data['m2m_field_names']:
            for obj in get_queryset(model_data['model']):
                if my_object.pk in [m2.pk for m2 in getattr(obj, field).all()]:
                    referencing_objects.append(obj)
    return referencing_objects
