documentation builder
-----------------------

This Django app adds a Django `management command <http://docs.djangoproject.com/en/dev/howto/custom-management-commands/>`_ to build the sphinx documentation for your project. Add ``'threespot.documentation'`` to your ``INSATLLED_APPS`` setting and run the command thusly::
    
    $>./manage.py build_docs

By default, it will search for docs in a folder call 'docs' in the project 
root and publish them to a folder called 'docs' in the ``MEDIA_ROOT`` of 
your settings file. You can override these with the following project
settings::

    DOCUMENTATION_PUBLISH_PATH = '/path/to/publish/to/'
    DOCUMENTATION_SOURCE_LOCATION = '/docs/source/path/'
