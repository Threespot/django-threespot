from copy import deepcopy
from itertools import chain

from django import template
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin.util import get_deleted_objects, unquote
from django.contrib.contenttypes import generic
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import models, transaction, router
from django.db.models.fields.related import RelatedField, ManyToManyField
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.encoding import force_unicode
from django.utils.functional import update_wrapper
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from threespot.orm.introspect import get_referencing_objects, \
    get_generic_referencing_objects, lookup_referencing_object_relationships
from threespot.workflow.app_settings import UNPUBLISHED_STATES, \
    PUBLISHED_STATE, USE_DJANGO_REVERSION


if USE_DJANGO_REVERSION:
    import reversion
    from reversion.admin import VersionAdmin
    AdminParentClass = VersionAdmin
    create_on_success = reversion.revision.create_on_success
else:
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
    slug_field = 'slug'
    slug = False
    
    def __init__(self, *args, **kwargs):
        """
        Intelligently determine if there is a slug field.
        """
        super(WorkflowAdmin, self).__init__(*args, **kwargs)
        for field in self.model._meta.fields:
            if field.__class__ == models.fields.SlugField \
                or issubclass(field.__class__, models.fields.SlugField):
                self.slug_field = field.name
                self.slug = True

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

    def has_publish_permission(self, request):
        permission = "%s.modify_published_pages" % self.model._meta.app_label
        return request.user.has_perm(permission)
    
    def add_view(self, request, form_url='', extra_context=None):
        """
        Wrap the add view to do permissions checking.
        """
        if request.method == 'POST' and not request.user.is_superuser:
            if not self.has_publish_permission(request):
                if request.POST.get('status') == PUBLISHED_STATE:
                    raise PermissionDenied((
                        "You do not have permission to publish %s objects."
                    ) % self.model._meta.verbose_name)
        else:
            extra_context = extra_context or {}
            extra_context.update({
                'no_publish_perm': not self.has_publish_permission(request)
            })
        return super(WorkflowAdmin, self).add_view(request,
            form_url=form_url,
            extra_context=extra_context
        )

    def change_view(self, request, object_id, extra_context=None):
        """
        Wrap the change view to do permissions checking.
        """
        if request.method == 'POST' and not request.user.is_superuser:
            if not self.has_publish_permission(request):
                # This check is less comprehensive than the following one, but
                # it requires no database lookup of the original object.
                if request.POST.get('status') == PUBLISHED_STATE:
                    raise PermissionDenied((
                        "You do not have permission to publish %s objects "
                        "or edit published objects."
                    ) % self.model._meta.verbose_name)
                # Lookup the object pre-change and see if it was alreay 
                # published. If so: permission denied.
                obj = self.get_object(request, unquote(object_id))
                if obj.is_published():
                    raise PermissionDenied((
                        "You do not have permission to edit published %s"
                        " objects."
                    ) % self.model._meta.verbose_name)
        else:
            extra_context = extra_context or {}
            extra_context.update({
                'no_publish_perm': not self.has_publish_permission(request)
            })
        return super(WorkflowAdmin, self).change_view(request, object_id,
            extra_context=extra_context
        )

    def changelist_view(self, request, extra_context=None):
        if not self.has_publish_permission(request):
            action_index = int(request.POST.get('index', 0))
            action_list = request.POST.getlist('action')
            if action_list and action_list[action_index] == 'delete_selected':
                selected_ids = request.POST.getlist(
                    helpers.ACTION_CHECKBOX_NAME
                )
                name = len(selected_ids) > 1 and "these items" or "this item"
                for obj_id in selected_ids:
                    obj = get_object_or_404(self.model, id=obj_id)
                    if obj.is_published():
                        change_list_url = reverse("admin:%s_%s_changelist" % (
                            obj._meta.app_label, obj._meta.module_name
                        ))
                        if len(selected_ids) > 1:
                            msg = (
                                "You do not have permission to delete these "
                                " items: at least one is already published."
                            )
                        else:
                            msg = (
                                "You do not have permission to delete this "
                                " item: it is already published."
                            )
                        self.message_user(request, msg)
                        return HttpResponseRedirect(change_list_url)
        return super(WorkflowAdmin, self).changelist_view(request, 
            extra_context=extra_context
        )

    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        if obj.is_published and not self.has_publish_permission(request):
            change_list_url = reverse("admin:%s_%s_changelist" % (
                obj._meta.app_label, obj._meta.module_name
            ))
            msg = (
                "You do not have permission to delete this item: it is "
                " already published."
            )
            self.message_user(request, msg)
            return HttpResponseRedirect(change_list_url)
        return super(WorkflowAdmin, self).delete_view(request, object_id, 
            extra_context=extra_context
        )

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
        object_refs = None

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
            if obj.is_draft_copy():
                self.message_user(
                    request, 
                    _('You cannot copy a draft copy.')
                )            
                return HttpResponseRedirect(request.path)
            if obj.get_draft_copy():
                self.message_user(
                    request, 
                    _('A draft copy already exists.')
                )
                return HttpResponseRedirect(request.path)
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
            generic_refs = get_generic_referencing_objects(obj)
            direct_refs = get_referencing_objects(obj)
            object_refs = [(unicode(o), o._meta.verbose_name) for o in \
                chain(direct_refs, generic_refs)
            ]
            
        context = {
            "title": title,
            "object_name": force_unicode(opts.verbose_name),
            "object": obj,
            "referencing_objects": object_refs,
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

        if not obj.is_draft_copy:
            return HttpResponseBadRequest(_(
                'The %s object could not be merged because it is not a'
                'draft copy. There is nothing to merge it into.'
            ) % force_unicode(opts.verbose_name))

        # Populate deleted_objects, a data structure of all related objects
        # that will also be deleted when this copy is deleted.
        generic_refs = get_generic_referencing_objects(obj.copy_of)
        direct_refs = get_referencing_objects(obj.copy_of)
        direct_refs = filter(lambda o: obj != o, direct_refs)
        object_refs = [(unicode(o), o._meta.verbose_name) for o in \
            chain(direct_refs, generic_refs)
        ]
        perms_needed = False
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
            "referencing_objects": object_refs,
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
        if self.slug:
            slug = getattr(new_item, self.slug_field)
            slug += "-draft-copy"
            setattr(new_item, self.slug_field, slug)
        new_item.save()
        fk_rels = [f.name for f in self.model._meta.fields \
            if issubclass(f.__class__, RelatedField) and f.name != 'copy_of'
        ]
        for field in fk_rels:
            setattr(new_item, field, getattr(item, field))
        m2m_rels = [f.name for f, _ in self.model._meta.get_m2m_with_model()]
        for field in m2m_rels:
            setattr(new_item, field, getattr(item, field).all())
        new_item.save()
        return new_item
        
    def _merge_item(self, original, draft_copy):
        """ Delete original, clean up and publish copy."""
        # Handle FK and M2M references.
        refs = filter(
            lambda obj: obj != draft_copy,
            get_referencing_objects(original)
        )
        for ref in refs:
            field_names = lookup_referencing_object_relationships(original, ref)
            for field_name in field_names:
                fld_class = ref._meta.get_field(field_name).__class__
                if issubclass(fld_class, models.fields.related.ManyToManyField):
                    getattr(ref, field_name).remove(original)
                    getattr(ref, field_name).add(draft_copy)
                else:
                    setattr(ref, field_name, draft_copy)
                    ref.save()
        # Handle generic references.
        for ref in get_generic_referencing_objects(original):
            generic_fk_field = [f for f in ref._meta.virtual_fields \
                if isinstance(f, generic.GenericForeignKey)
            ][0].name
            setattr(ref, generic_fk_field, draft_copy)
            ref.save()
        # Overwrite the old object.
        setattr(original, self.slug_field, original.slug + "-merge")
        original.save()
        if self.slug:
            import re
            slug = re.sub(
                "-draft-copy$", "", getattr(draft_copy, self.slug_field)
            )
            setattr(draft_copy, self.slug_field, slug)
        draft_copy.copy_of = None
        draft_copy.save()
        original.delete()
        draft_copy.publish()
        return draft_copy

    def publish_items(self, request, queryset):
        """ Admin action publishing the selected items."""
        # We should exclude any draft copies: these can only be published 
        # through merging.
        original_length = len(queryset)
        rows_updated = queryset.filter(copy_of__exact=None).update(
            status=PUBLISHED_STATE
        )
        if rows_updated == 1:
            message = "One item was successfully published."
        else:
            message = "%d items were successfully published." % rows_updated
        if original_length != rows_updated:
            message += (
                " Any draft copies selected were not published; to publish "
                " these, merge them into the original."
            )
        self.message_user(request, message)
    publish_items.short_description = "Publish selected items"

    def unpublish_items(self, request, queryset):
        """ Admin action publishing the selected items."""
        rows_updated = queryset.update(status=UNPUBLISHED_STATES[0][0])
        if rows_updated == 1:
            message = "One item was successfully unpublished."
        else:
            message = "%d items were successfully unpublished." % rows_updated
        self.message_user(request, message)
    unpublish_items.short_description = "Unpublish selected items"