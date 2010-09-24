from types import ClassType
from django.db.models.manager import Manager
from django.db.models.query import QuerySet

"""
Easier custom Model Manager Chaining
http://djangosnippets.org/snippets/2117/
Example Usage:

from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

class AuthorMixin(object):
    def by_author(self, user):
        return self.filter(user=user)

class PublishedMixin(object):
    def published(self):
        return self.filter(published__lte=datetime.now())

def unpublished(self):
    return self.filter(published__gte=datetime.now())

class CustomManager(Manager):
    def get_query_set(self):
        return super(CustomManager, self).get_query_set().order_by('-published')

class Post(models.Model):
    user = models.ForeignKey(User)
    published = models.DateTimeField()

    objects = manager_from(AuthorMixin, PublishedMixin, unpublished,
                              manager_cls=CustomManager)


"""


def manager_from(*mixins, **kwds):
    '''
    Returns a Manager instance with extra methods, also available and
    chainable on generated querysets.

    :param mixins: Each ``mixin`` can be either a class or a function. The
        generated manager and associated queryset subclasses extend the mixin
        classes and include the mixin functions (as methods).

    :keyword queryset_cls: The base queryset class to extend from
        (``django.db.models.query.QuerySet`` by default).

    :keyword manager_cls: The base manager class to extend from
        (``django.db.models.manager.Manager`` by default).
    '''
    # collect separately the mixin classes and methods
    bases = [kwds.get('queryset_cls', QuerySet)]
    methods = {}
    for mixin in mixins:
        if isinstance(mixin, (ClassType, type)):
            bases.append(mixin)
        else:
            try: methods[mixin.__name__] = mixin
            except AttributeError:
                raise TypeError('Mixin must be class or function, not %s' %
                                mixin.__class__)
    # create the QuerySet subclass
    id = hash(mixins + tuple(kwds.iteritems()))
    new_queryset_cls = type('Queryset_%d' % id, tuple(bases), methods)
    # create the Manager subclass
    bases[0] = manager_cls = kwds.get('manager_cls', Manager)
    new_manager_cls = type('Manager_%d' % id, tuple(bases), methods)
    # and finally override new manager's get_query_set
    super_get_query_set = manager_cls.get_query_set
    def get_query_set(self):
        # first honor the super manager's get_query_set
        qs = super_get_query_set(self)
        # and then try to bless the returned queryset by reassigning it to the
        # newly created Queryset class, though this may not be feasible
        if not issubclass(new_queryset_cls, qs.__class__):
            raise TypeError('QuerySet subclass conflict: cannot determine a '
                            'unique class for queryset instance')
        qs.__class__ = new_queryset_cls
        return qs
    new_manager_cls.get_query_set = get_query_set
    return new_manager_cls()