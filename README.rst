===========
Sekretariat
===========

Aplikacja pomagająca w organizacji pracy sektretariat szkoły


.. image:: https://img.shields.io/pypi/v/sekretariat.svg
        :target: https://pypi.python.org/pypi/sekretariat

.. image:: https://img.shields.io/travis/wooyek/sekretariat.svg
        :target: https://travis-ci.org/wooyek/sekretariat

.. image:: https://readthedocs.org/projects/sekretariat/badge/?version=latest
        :target: https://sekretariat.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
.. image:: https://coveralls.io/repos/github/wooyek/sekretariat/badge.svg?branch=develop
        :target: https://coveralls.io/github/wooyek/sekretariat?branch=develop
        :alt: Coveralls.io coverage

.. image:: https://codecov.io/gh/wooyek/sekretariat/branch/develop/graph/badge.svg
        :target: https://codecov.io/gh/wooyek/sekretariat
        :alt: CodeCov coverage

.. image:: https://api.codeclimate.com/v1/badges/0e7992f6259bc7fd1a1a/maintainability
        :target: https://codeclimate.com/github/wooyek/sekretariat/maintainability
        :alt: Maintainability

.. image:: https://img.shields.io/github/license/wooyek/sekretariat.svg
        :target: https://github.com/wooyek/sekretariat/blob/develop/LICENSE
        :alt: License

.. image:: https://img.shields.io/twitter/url/https/github.com/wooyek/sekretariat.svg?style=social
        :target: https://twitter.com/intent/tweet?text=Wow:&url=https://github.com/wooyek/sekretariat
        :alt: Tweet about this project

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
        :target: https://saythanks.io/to/wooyek


* Free software: GNU Affero General Public License v3
* Documentation: https://sekretariat.readthedocs.io.

Features
--------

* Pending :D

Demo
----

To run an example project for this django reusable app, click the button below and start a demo serwer on Heroku

.. image:: https://www.herokucdn.com/deploy/button.png
    :target: https://heroku.com/deploy
    :alt: Deploy Django Opt-out example project to Heroku


Quickstart
----------

1. Fork the `sekretariat` repo on `https://github.com/wooyek/sekretariat`
2. Clone your fork locally::

    $ git clone git@github.com:wooyek/sekretariat.git

3. Setup your development env::

    $ pipsi install pew
    $ cd sekretariat/
    $ pew new -p python3 -a $(pwd) $(pwd | xargs basename)
    $ pew workon sekretariat
    $ pip install -r requirements/development.txt

4. Test project health::

    $ python manage.py check
    $ pytest
    $ inv check
    $ tox

5. Initialize development database and fill it with test data::

    $ bash bin/database_create.sh
    $ inv db

6. Create a branch for local development and start development server::

    $ git checkout -b name-of-your-bugfix-or-feature
    $ python manage.py runserver


Deployment
----------

Add a development remote and deploy::

    $ git remote add dev https://git.heroku.com/sekretariat-dev.git
    $ inv deploy

Credits
-------

This package was created with Cookiecutter_ and the `wooyek/cookiecutter-django-app`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`wooyek/cookiecutter-django-app`: https://github.com/wooyek/cookiecutter-django-app
.. _`pipenv`: https://docs.pipenv.org/install
.. _`Dokku PaaS`: http://dokku.viewdocs.io/dokku/getting-started/installation/
