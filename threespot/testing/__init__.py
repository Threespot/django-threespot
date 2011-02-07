from django.core.urlresolvers import reverse
from django.db import models
from django.test import TestCase

class TestCasePlus(TestCase):
    
    """
    Provides simple helpers for writing Django tests.
    """
    
    def assert_object_in_context(url, context_name, obj):
        """
        A test case to determine if the object that exists with the given 
        ``context_name`` at the specified URL is the same as ``obj``.  
        """
        result = self.client.get(url)
        # Verify the URL comes back with a status code of 200.
        self.assertEqual(result.status_code, 200)
        # Verofy the context has the value.
        self.assertTrue(result.context.has_key(context_name))
        context_object = result.context[context_name]
        # Verify object and context object are instances of the same class.
        self.assertTrue(context_object.__class__, obj.__class__)
        # If the objects are instances of a Django model, verify they have the 
        # same primary key.
        if issubclass(obj.__class__, models.Model):
             self.assertEqual(context_object.pk, obj.pk)   