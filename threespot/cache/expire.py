from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.utils.cache import get_cache_key
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote

"""
This module contains functions for expiring higher-level django caches.
"""

def expire_view_cache(view_name, args=[], kwargs={}, namespace=None,\
    key_prefix=None):
    """
    This function allows you to invalidate any view-level cache. 
    
    :param view_name: view function to invalidate or its named url pattern
    
    :keyword args: any arguments passed to the view function
    
    :keyword namepace: if an application namespace is used, pass that
    
    :keyword key_prefix: the @cache_page decorator for the function (if any)
    
    """

    # create a fake request object
    request = HttpRequest()
    # Loookup the request path:
    if namespace:
        view_name = namespace + ":" + view_name
    request.path = reverse(view_name, args=args)
    # get cache key, expire if the cached item exists:
    key = get_cache_key(request, key_prefix=key_prefix)
    if key:
        if cache.get(key):
            cache.set(key, None, 0)
        return True
    return False


def invalidate_template_cache2(fragment_name, *variables):
    """
    From http://djangosnippets.org/snippets/1593/
    
    This function invalidates a template-fragment cache bit.

    say you have:

    {% load cache %}
    {% cache 600 user_cache user.id %} something expensive here {% endcache %}

    To invalidate:

    invalidate_template_cache("user_cache", user.id)
    """
    args = md5_constructor(u':'.join([urlquote(unicode(v)) for v in variables]))
    cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
    cache.delete(cache_key)
    return cache_key
