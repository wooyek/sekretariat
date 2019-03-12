=====
Usage
=====

TODO: Modify this template in wooyek/cookiecutter-django-website for django project installation


To use Sekretariat in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'sekretariat.apps.SekretariatConfig',
        ...
    )

Add Sekretariat's URL patterns:

.. code-block:: python

    from sekretariat import urls as sekretariat_urls


    urlpatterns = [
        ...
        url(r'^', include(sekretariat_urls)),
        ...
    ]
