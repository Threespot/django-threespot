===================
Workflow App
===================

What this django application is good for
------------------------------------------------------------------

The ``threespot.workflow`` app provides a simple workflow for models. It helps with previewing content, and supports applying different states to a piece of
content (e.g. "Draft" or "Preview").

What this django application is (probably) not good for
------------------------------------------------------------------

If you need a heavyweight workflow--editorial queues, version control, branching and merging of content, that sort of stuff--than look elsewhere; workflow is likely not for you. And unless you are building a CMS for a *big* team, rethink if you really do need that stuff.

Installing
-----------

Assuming you have Threespot installed somewhere, all you have to do is install the app in your settings::

    INSTALLED_APPS = (
        'django.contrib.auth',
        [...]
        'threespot.workflow',
    )

At this point, nothing will happen. You have to decide what models *need* a workflow. Let's imagine a hypothetical app called "publications" with a model called "Article" that we want to have workflow features. Here's how we'd go 
about doing that.

Add workflow mixin to model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In our 'publications.models' module, we'll modify the ``Article`` model definition to include the ``WorkflowMixin`` class::

    from django.db import models
    from threespot.workflow.models import WorkflowMixin

    class Article(WorkflowMixin, models.Model):
        slug = models.SlugField()
        title = models.CharField(max_legth=255)
        
Subclass your model admin with the ``WorkflowAdmin`` class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In our ``publications.admin`` module, we'll modify our ``ArticleAdmin``  definition to subclass the ``WorkflowAdmin`` class::

    from threespot.workflow.admin import WorkflowAdmin

    from forms import ArticleAdminForm

    class ArticleAdmin(WorkflowAdmin):
        form = ArticleAdminForm

If you're using a custom ``ModelForm`` for your modeladmin (as we are above), then you will also want to subclass *that* with the ``WorkflowAdminFormMixin``::

    from django import forms
    from threespot.workflow.forms import WorkflowAdminFormMixin
    
    from models import Article
    
    class ArticleAdminForm(WorkflowAdminFormMixin, forms.ModelForm):

        class Meta:
            model = Article

And that's it. Workflow is now in place for the article model...just about. There are some settings you can fiddle with in your project settings file.

Available settings
-------------------


WORKFLOW_WORKFLOW_CHOICES
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``(('d', 'Draft'), ('p', 'Published'),)``

This setting defines the states that an object with a workflow can have. By default, content has a status of either 'draft' or 'published' but you can add
other status types as you like, using this setting.

WORKFLOW_PUBLISHED_STATE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``'p'``

Although you can have as many status items as you want, only one can correspond to the published state. This is state in the workflow choices that means a piece of content is published. 

WORKFLOW_USE_DJANGO_REVERSION
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``False``

In a nod to more heayweight versioning, you can tell workflow to use django-reversions for models it manages as well. It's up to you to install that package, but if you have it installed, setting this to ``True`` will add versioning to all you workflow-managed models.

Options for the admin model
----------------------------

There are a also a few options pertaining to the admin which you can set on the modeladmin instance that subclasses the ``WorkflowAdmin`` class::

    class ArticleAdmin(WorkflowAdmin):
        form = ArticleAdminForm
        m2m_relations_to_copy = ['related_grants']
        slug = True
        slug_field = 'slug'

m2m_relations_to_copy
^^^^^^^^^^^^^^^^^^^^^^

When it creates a draft copy of a piece of published content, threespot.workflow does not copy many-to-many relationships to other models on the source model. Include the names of the many-to-many model fields you want to copy to the draft copy in the ``m2m_relations_to_copy`` attribute.

slug
^^^^^^^^^^^^^^^^^^^^^^

If your model uses a slug field to do lookups outside the admin, set this to ``True`` (it's assumed to be false otherwise). This will cause threespot.workflow to modify the slug of draft copies to avoid duplicate lookup exceptions when you do ``Article.objects.get(slug='slug-name')``.

slug_field
^^^^^^^^^^^^^^^^^^^^^^
The name of the slug field on you model (assumed to be 'slug' unless you set this.)

ToDo
-----

Document the ``published_object_detail`` generic view and the model and manager methods workflow gives you (in the mean time, all of these are clearly documented in the docstrings).

