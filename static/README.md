Static files
------------

The files in this folder are served in production, together with other static
files provided by Django packages directly by Apache.

Do not add by hand files to the path configured in ``static_root``
(see: ``/etc/camt/config.json``), with the next deployment they will be deleted!

The command ``manage.py collectstatic --clear`` copies the files there. The
setting ``STATIC_ROOT`` in ``settings.py`` configures these paths. Existing
files in ``STATIC_ROOT`` location are deleted!

If you run ``manage.py runserver`` locally on your laptop ensure that the
setting ``DEBUG = True`` is active, because then Django will serve these files
directly from this ``static`` folder.

In all cases the browser is requesting the files from http://host/static/*
path (``STATIC_URL = '/static/'`` setting).

In templates use the ``static`` tag, e.g like this:
``{% static 'css/bootstrap.min.css' %}``

See also:
  * https://docs.djangoproject.com/en/1.11/howto/static-files/
  * https://docs.djangoproject.com/en/1.11/ref/contrib/staticfiles/
  * https://docs.djangoproject.com/en/1.11/howto/static-files/deployment/
