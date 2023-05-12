============
Django Ranks
============

Not ready yet, DO NOT USE

Django Ranks is a Django app to conduct web-based Django Ranks. For each question,
visitors can choose between a fixed number of answers.

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

