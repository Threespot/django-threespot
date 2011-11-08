from django.core.urlresolvers import reverse
from django.db import models
from django.test import TestCase

class TestCasePlus(TestCase):
    
    """
    Provides simple helpers for writing Django tests.
    """
    
    def assert_object_in_context(self, url, context_name, obj):
        """
        A test case to determine if the object that exists with the given 
        ``context_name`` at the specified URL is the same as ``obj``.  
        """
        result = self.client.get(url)
        # Verify the URL comes back with a status code of 200.
        self.assertEqual(result.status_code, 200)
        # Verify the context has the value.
        self.assertTrue(context_name in result.context)
        context_object = result.context[context_name]
        # Verify object and context object are instances of the same class.
        self.assertTrue(context_object.__class__, obj.__class__)
        # If the objects are instances of a Django model, verify they have the 
        # same primary key.
        if issubclass(obj.__class__, models.Model):
             self.assertEqual(context_object.pk, obj.pk)

     def verify_status_code_response(self, url, code):
         """
         Verify that a GET request to the given URL returns the given status 
         code.
         """
         response = self.client.get(url)
         if response.status_code != code:
             raise AssertionError((
                 "The url '%s' returned a %d status code, not a %d."
             ) % (url, response.status_code, code))
         return response        

     def verify_200_response(self, url):
         """
         Shortcut function: verify that a GET request to the given URL returns 
         an "OK" (200) status code.
         """
         return self.verify_status_code_response(url, 200)

     def verify_301_response(self, url):
         """
         Shortcut function: verify that a GET request to the given URL returns 
         a "Moved Permanently" (301) status code.
         """         
         return self.verify_status_code_response(url, 301)

     def verify_302_response(self, url):
         """
         Shortcut function: verify that a GET request to the given URL returns 
         a "Found" (302) status code.
         """
         return self.verify_status_code_response(url, 302)

     def verify_404_response(self, url):
         """
         Shortcut function: verify that a GET request to the given URL returns 
         a "Not Found" (404) status code.
         """
         return self.verify_status_code_response(url, 404)    