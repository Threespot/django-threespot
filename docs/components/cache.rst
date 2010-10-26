Caching Utilities
==================

This module contains utilities that make Django's caching framework easier to use.

expire
-------

This module contains functions for expiring higher-level django caches.


expire_view_cache
^^^^^^^^^^^^^^^^^^^^

This function allows you to invalidate any view-level cache. 

The function takes the following argument:

* *view_name*: view function to invalidate or its named url pattern

...and the following keyword arguments:

* *args*: any arguments passed to the view function
* *namespace*: if an application namespace is used, pass that
* *keyword key_prefix*: the @cache_page decorator for the function (if any)

Usage::

    @cache_page(60)
    def my_view(request, user_id):
        user = User.objects.get(id=user_id)
        return HttpResponse("Hello, %s." % user.fullname)

    def expire_all_myview():
       for user in User.objects.all():
            expire_view_cache('myapp.myview', user.id)

invalidate_template_cache
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This function invalidates a template-fragment cache bit. Sourced from `Djangosnippets <http://djangosnippets.org/snippets/1593/>`_.

say you have the following in a template file::

    {% load cache %}
    {% cache 600 user_cache user.id %} something expensive here {% endcache %}

To invalidate it::

    invalidate_template_cache("user_cache", user.id)
