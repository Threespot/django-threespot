import re

from django import template
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

register = template.Library()

_phone_num = re.compile("^(\d{3})(\d{3})(\d{4})(.*)")
_email = re.compile("([\w\-][\w\-\.]+)@([\w\-]+)\.([a-zA-Z]{2,4})")

def phonenumber(value):
    """
    Converts an integer to a US-formatted phone number.
    """
    orig = force_unicode(value)
    return _phone_num.sub("(\g<1>) \g<2>-\g<3>\g<4>", orig)

phonenumber.is_safe = True
register.filter(phonenumber)

def safe_email(value):
    """
    Replace an email address with ""{name} at {domain} dot {suffix}" inside a 
    span tag with the class "safe-email". The following script will reverse 
    this (assumes you have jQuery):
    
    <script type="text/javascript">
    $("span.safe-email").each(function () { 
        var email = $(this).text().replace(" at ", "@").replace(" dot ", ".");
        var link = $('<a href="mailto:' + email + '">' + email + '</a>');
        $(this).after(link).remove();
    })
    </script>
    """
    orig = force_unicode(value)
    return mark_safe(_email.sub(
        "<span class=\"safe-email\">\g<1> at \g<2> dot \g<3></span>",
        orig
    ))

register.filter(safe_email)