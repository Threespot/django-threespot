from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

from palettes import full_pallete

CKEDITOR_PATH = getattr(settings, 'THREESPOT_CKEDITOR_PATH', '') 
if not CKEDITOR_PATH.endswith("/"):
    CKEDITOR_PATH += "/"

class CKEditor(forms.Textarea):
    """A richtext editor widget that uses CKEditor.
    Inspired by http://code.google.com/p/django-ck
    """
    additional_plugins_js = ''
    
    class Media:
        js = (
            CKEDITOR_PATH + 'ckeditor.js',
            CKEDITOR_PATH + 'adapters/jquery.js',
        )
        css = {
        }

    def __init__(self, *args, **kwargs):
        
        self.ck_attrs = kwargs.get('ck_attrs', {})
        if self.ck_attrs:
            kwargs.pop('ck_attrs')
        
        self.additional_plugins_js = kwargs.get('additional_plugins_js', '')
        if self.additional_plugins_js:
            kwargs.pop('additional_plugins_js')

        self.pallete = kwargs.get('custom_pallete', full_pallete)
        if kwargs.get('custom_pallete'):
            kwargs.pop('custom_pallete')
        
        super(CKEditor, self).__init__(*args, **kwargs)
        
    def _serialize_script_params(self):
        # If the width attribute of the widget is set, we'll need to add a 
        # hack for webkit browsers, otherwise, CKEditor toolbar floats will
        # not clear properly. 
        if self.ck_attrs.has_key('width'):
            self.webkit_css_hack = "{ width: %s; }" % self.ck_attrs['width']
        else:
            self.webkit_css_hack = ''
        ck_attrs = ''
        if not 'language' in self.ck_attrs:
            self.ck_attrs['language'] = get_language()[:2]
        dict_items = []
        for k,v in self.ck_attrs.iteritems():
            dict_items.append(k + " : '" + v + "'")
        ck_attrs += ",\n".join(dict_items)
        return ck_attrs
    
    def render(self, name, value, attrs=None):
        template = """%(field)s
        <style type="text/css"> label[for=id_%(field_name)s] { padding: 0 0 4px 4px; float: none; width: auto;} %(webkit_css_hack)s</style>
        <script type="text/javascript">
            var %(field_variable_name)s_CKeditor = new CKEDITOR.replace('id_%(field_name)s', {
                %(options)s,
                toolbar : [
                    %(pallete)s,
                    %(additional_plugins_js)s
                ]
            });
        </script>"""
        opts = self._serialize_script_params()
        if self.webkit_css_hack:
            self.webkit_css_hack = (
                ".%s .cke_toolbox %s"
            ) % (name, self.webkit_css_hack)
        return mark_safe(template % {
            'additional_plugins_js': mark_safe(self.additional_plugins_js),
            'field': super(CKEditor, self).render(name, value, attrs),
            'field_name': name,
            'field_variable_name': name.replace("-", "_"),
            'options': opts,
            'pallete': self.pallete,
            'webkit_css_hack': self.webkit_css_hack
        })
