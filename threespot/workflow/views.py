from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import ObjectDoesNotExist
from django.core.xheaders import populate_xheaders
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.utils.http import urlquote


def published_object_detail(request, queryset, object_id=None, slug=None,
        slug_field='slug', template_name=None, template_name_field=None,
        template_loader=loader, extra_context=None,
        context_processors=None, template_object_name='object',
        mimetype=None):
    """
    This view has the same function signature and behavior as 
    ``views.generic.list_detail.object_detail`` with one exception:
    
    This view verifies that a user is staff if the object is not published.
    If the user is not staff and the content is not published, they are 
    redirected to login. If they are, the additional ``is_preview`` context 
    in the template will be ``True``.
    """
    if extra_context is None: extra_context = {}
    model = queryset.model
    if object_id:
        queryset = queryset.filter(pk=object_id)
    elif slug and slug_field:
        queryset = queryset.filter(**{slug_field: slug})
    else:
        raise AttributeError((
            "Generic detail view must be called with either an object_id or "
            "a slug/slug_field."
        ))
    
    response = None
    try:
        obj = queryset.get()
    except ObjectDoesNotExist:
        if request.user.is_staff:
            response = "not_found"
        else:
            response = "redirect"
    else:
        if not obj.is_published() and not request.user.is_staff:
                response = "redirect"
    
    if response:
        if response == 'redirect':
            path = urlquote(request.get_full_path())
            tup = settings.LOGIN_URL, REDIRECT_FIELD_NAME, path
            return HttpResponseRedirect('%s?%s=%s' % tup)
        if response == 'not_found':
            raise Http404(
                "No %s found matching the query" % (model._meta.verbose_name)
            )
    
    extra_context['is_preview'] = not obj.is_published()
            
    if not template_name:
        template_name = "%s/%s_detail.html" % (
            model._meta.app_label, 
            model._meta.object_name.lower()
        )
    if template_name_field:
        template_name_list = [getattr(obj, template_name_field), template_name]
        t = template_loader.select_template(template_name_list)
    else:
        t = template_loader.get_template(template_name)
    
    c = RequestContext(
        request, 
        {template_object_name: obj,}, 
        context_processors
    )
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    response = HttpResponse(t.render(c), mimetype=mimetype)
    populate_xheaders(
        request, 
        response, 
        model, 
        getattr(obj, obj._meta.pk.name)
    )
    return response