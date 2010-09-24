from django.http import Http404

"""
Add the breadcrumb to your context processors in the project settings:

>>> TEMPLATE_CONTEXT_PROCESSORS = (
...        "threespot.nav.context_processors.breadcrumb",
... )

Then simply decorate your view functions:

>>> from django.http import HttpResponse
>>> from threespot.nav import breadcrumb
>>>
>>> @breadcrumb(breadcrumb="Homepage")
... def index(request):
...    return HttpResponse("Hello, world.")

The context processor will use these decorators as it crawls up the
URL tree. If the previous view function lives at the url `/`, we could
define a second view function for a url like `/123/` where `123` is a 
parameter to the view:

>>> @breadcrumb(breadcrumb=lambda id: Article.objects.get(pk=id).title)
... def article(request, id):
...    title = Article.objects.get(pk=id).title
...    return HttpResponse("The title of this article is %s." % title)

Note that you can define a breadcrumb as a callable, as is done above. 

The template for the article view would have the following `breadcrumb` variable
in it's context:

>>> (('/', 'Homepage',), ('/123/', 'My Title',),)

...which could be templated thusly:

<ul>
{%for url, crumb in breadcrumb%}
    <li><a href="{{url}}">{{crumb}}</a></li>
{%endfor%}
</ul> 
 

"""

def breadcrumb(request):
    """
    A context processor that returns a context variable representing a 
    breadcrumb.
    """
    from urlparse import urljoin
    from django.core import urlresolvers
    from django.utils.http import urlquote
    try:
        from settings import BREADCRUMB_IGNORE_PATH
    except ImportError:
       BREADCRUMB_IGNORE_PATH = None
    urls = []
    
    def parseURL(url):
        """recursively shorten url"""
        if url != "/":
            urls.insert(0, url)
            parseURL(urljoin(url, '..'))
    
    path = BREADCRUMB_IGNORE_PATH and \
        request.path.replace(BREADCRUMB_IGNORE_PATH, '') or request.path
    parseURL(path)
    # Get view for specified url.
    resolver = urlresolvers.get_resolver(None)
    breadcrumbs = []
    crumblessViews = []
    for url in urls:
        try:
            callback, callback_args, callback_kwargs = resolver.resolve(url)
        except Http404:
            #URL does not have a view, which means no breadcrumb either.
            crumblessViews.append(url)                
        else:
            #Check if view has a breadcrumb property.
            crumb = getattr(callback, 'breadcrumb', None)
            if crumb:
                #if the breadrumb is a callable object, call it, passing 
                # kwargs...
                crumb = hasattr(crumb, '__call__') and \
                    crumb.__call__(**callback_kwargs) or crumb
                # ...if not, just append to the list of breadcrumbs...
                breadcrumbs.append(crumb)
            else:
                #...otherwise, add to urls with no breadcrumb.
                crumblessViews.append(url)
    [urls.remove(url) for url in crumblessViews]
    if BREADCRUMB_IGNORE_PATH:
        urls = [BREADCRUMB_IGNORE_PATH + url for url in urls]
    return {'breadcrumb': zip(urls, breadcrumbs)}