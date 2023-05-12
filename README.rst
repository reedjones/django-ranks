============
Django Ranks
============

Not ready yet, DO NOT USE - but check back soon 🤠

Django Ranks is a generic Django app to 'rank' models with OpenSkill.py https://github.com/OpenDebates/openskill.py


INSTALL -

pip install django-ranks

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "Django Ranks" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "django_ranks",
    ]

2. Include the Django Ranks URLconf in your project urls.py like this::

    path("ranks/", include("django_ranks.urls")),

3. Run ``python manage.py migrate`` to create the Django Ranks models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

