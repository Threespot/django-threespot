==================================
Admin template tags and filters
==================================

To use the template tags provided in this module, it is necessary to add
``threespot.admin`` to your installed apps.


Using tags in a template
-------------------------

Add ``{%load admin_introspection%}`` to your template.

.. highlightlang:: html+django

app_label
~~~~~~~~~~~~~~~

Gets the application label for a model instance. 

For example::

    {{ item|app_label }}

If ``item`` is ``<Tag: Ipsum>``, the output will be ``tags``, if ``Tag`` is a model in the application ``tags``.

model_verbose_name
~~~~~~~~~~~~~~~~~~~

Gets the verbose name label for a model instance.

For example::

    {{ item|model_verbose_name }}

If ``item`` is ``<Tag: Ipsum>``, the output will be ``Tag``, if ``Tag`` is a model in the application ``tags``.

edit_object_url
~~~~~~~~~~~~~~~~~~~~

Gets the url to edit an item in the admin for a model instance.

For example::

    {{ item|edit_object_url }}

If ``item`` is ``<Tag: Ipsum>``, the output will be ``/admin/tags/tag/123``, if ``Tag`` is a model in the application ``tags`` with an id of 123.
