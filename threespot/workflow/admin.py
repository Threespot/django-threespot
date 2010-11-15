from copy import deepcopy
from itertools import chain

from django import template
from django.contrib import admin
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin.util import unquote, get_deleted_objects
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext_lazy as _

from app_settings import UNPUBLISHED_STATES, PUBLISHED_STATE, \
    USE_DJANGO_REVERSION

if USE_DJANGO_REVERSION:
    print "Goo!"
    import reversion
    from reversion.admin import VersionAdmin
    AdminParentClass = VersionAdmin
    create_on_success = reversion.revision.create_on_success
else:
    print "Bar!"
    AdminParentClass = admin.ModelAdmin
    def create_on_success(func):
        """A do-nothing replacement if we're not using django-reversion."""
        return func

class WorkflowAdmin(AdminParentClass):
    
    actions = ['publish_items', 'unpublish_items']
    change_form_template = "workflow/admin/change_form.html"
    copy_form_template = "workflow/admin/copy_confirmation.html"
    merge_form_template = "workflow/admin/merge_confirmation.html"
    exclude = ['copy_of']
    m2m_relations_to_copy = []
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        info = self.model._meta.app_label, self.model._meta.module_name
        
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urls = super(WorkflowAdmin, self).get_urls()
        workflow_urls = patterns('',
            url(r'^(.+)/copy/$', wrap(self.copy_view),
                name = '%s_%s_copy' % info
            ),
            url(r'^(.+)/merge/$', wrap(self.merge_view),
                name = '%s_%s_merge' % info
            ),
        )
        return workflow_urls + urls

    @csrf_protect_m
    @transaction.commit_on_success
    @create_on_success    
    def copy_view(self, request, object_id, extra_context=None):
        """
        Create a draft copy of the item after user has confirmed. 
        """
        opts = self.model._meta
        app_label = opts.app_label

        obj = self.get_object(request, unquote(object_id))    
    
        # For our purposes, permission to copy is equivalent to 
        # has_add_permisison.
        if not self.has_add_permission(request):
            raise PermissionDenied

        if obj is None:
            raise Http404(_(
                '%(name)s object with primary key %(key)r does not exist.') %   
                {
                    'name': force_unicode(opts.verbose_name), 
                    'key': escape(object_id)
                }
            )
    
        if request.POST: # The user has already confirmed the copy.
            obj_display = force_unicode(obj) + " copied."
            self.log_change(request, obj, obj_display)
            
            copy = self._copy_item(obj)

            self.message_user(
                request, 
                _('The %(name)s "%(obj)s" was copied successfully.') % {
                    'name': force_unicode(opts.verbose_name), 
                    'obj': force_unicode(obj_display)
                }
            )
            
            url = reverse(
                "admin:%s_%s_change" % (
                    app_label, 
                    self.model._meta.module_name
                ),
                args=(copy.id,)
            )
            return HttpResponseRedirect(url)

        if self.model.objects.filter(copy_of=obj).exists():
            draft_already_exists = True
            title = _("Draft Copy Exists")
            edit_copy_url = reverse(
                "admin:%s_%s_change" % (
                    app_label, 
                    self.model._meta.module_name
                ),
                args=(self.model.objects.filter(copy_of=obj)[0].id,)
            )
            
        else:
            draft_already_exists = False
            title = _("Are you sure?")
            edit_copy_url = None
        context = {
            "title": title,
            "object_name": force_unicode(opts.verbose_name),
            "object": obj,
            "opts": opts,
            "root_path": self.admin_site.root_path,
            "app_label": app_label,
            'draft_already_exists': draft_already_exists,
            'edit_copy_url': edit_copy_url
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(
            request, 
            current_app=self.admin_site.name
        )
        return render_to_response(self.copy_form_template, context, 
            context_instance=context_instance
        )    

    @csrf_protect_m
    @transaction.commit_on_success
    @create_on_success
    def merge_view(self, request, object_id, extra_context=None):
        """
        The 'merge' admin view for this model. Allows a user to merge a copy 
        back over the original.
        """
        opts = self.model._meta
        app_label = opts.app_label

        obj = self.get_object(request, unquote(object_id))
        
        # For our purposes, permission to merge is equivalent to 
        # has_change_permisison and has_delete_permission.
        if not self.has_change_permission(request, obj) \
            or not self.has_delete_permission(request, obj) :
            raise PermissionDenied

        if obj is None:
            raise Http404(_(
                '%(name)s object with primary key %(key)r does not exist.') %   
                {
                    'name': force_unicode(opts.verbose_name), 
                    'key': escape(object_id)
                }
            )

        # Populate deleted_objects, a data structure of all related objects
        # that will also be deleted when this copy is deleted.
        (deleted_objects, perms_needed) = get_deleted_objects(
            (obj.copy_of,), opts, request.user, self.admin_site
        )
        # Flatten nested list:
        deleted_objects = map(
            lambda i: hasattr(i, '__iter__') and i or [i],
            deleted_objects
        )
        deleted_objects = chain(*deleted_objects)
        deleted_objects = list(deleted_objects)
        
        if request.POST: # The user has already confirmed the merge.
            if perms_needed:
                raise PermissionDenied
            obj_display = force_unicode(obj) + " merged."
            self.log_change(request, obj, obj_display)
            
            original = obj.copy_of
            self._merge_item(original, obj)

            self.message_user(
                request, 
                _('The %(name)s "%(obj)s" was merged successfully.') % {
                    'name': force_unicode(opts.verbose_name), 
                    'obj': force_unicode(obj_display)
                }
            )

            return HttpResponseRedirect("../../")

        context = {
            "title": _("Are you sure?"),
            "object_name": force_unicode(opts.verbose_name),
            "object": obj,
            "escaped_original": force_unicode(obj.copy_of), 
            "deleted_objects": deleted_objects,
            "perms_lacking": perms_needed,
            "opts": opts,
            "root_path": self.admin_site.root_path,
            "app_label": app_label,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(
            request, 
            current_app=self.admin_site.name
        )
        return render_to_response(self.merge_form_template, context, 
            context_instance=context_instance
        )

    def _copy_item(self, item):
        """ Create a copy of a published item to edit."""
        if not item.is_published:
            return None
        new_item = deepcopy(item)
        new_item.id = None
        new_item.status = UNPUBLISHED_STATES[0][0]
        new_item.copy_of = item
        for field in ('name', 'title'):
            if hasattr(new_item, field):
                value = getattr(new_item, field) + " (draft copy)"
                setattr(new_item, field, value)
        new_item.save()
        for field in self.m2m_relations_to_copy:
            if hasattr(item, field):
                setattr(new_item, field, getattr(item, field).all())
        new_item.save()
        return new_item
        
    def _merge_item(self, original, copy):
        """ Delete original, clean up and publish copy."""
        for field in ('name', 'title'):
            if hasattr(copy, field):
                value = getattr(copy, field).replace(" (draft copy)", "")
                setattr(copy, field, value)
        copy.copy_of = None
        copy.save()
        original.delete()
        copy.publish()
        return copy

    def publish_items(self, request, queryset):
        """ Admin action publishing the selected items."""
        rows_updated = queryset.update(status=PUBLISHED_STATE)
        if rows_updated == 1:
            message = "One item was successfully published."
        else:
            message = "%d items were successfully published."
        self.message_user(request, message)
    publish_items.short_description = "Publish selected items"

    def unpublish_items(self, request, queryset):
        """ Admin action publishing the selected items."""
        rows_updated = queryset.update(status=UNPUBLISHED_STATES[0][0])
        if rows_updated == 1:
            message = "One item was successfully unpublished."
        else:
            message = "%d items were successfully unpublished."
        self.message_user(request, message)
    publish_items.short_description = "Unpublish selected items"