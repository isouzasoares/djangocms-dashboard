===================
DjangoCMS Dashboard
===================

A simple dashboard to manage DjangoCMS's plugins, apphooks, etc.,
all on the same place.
Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Install the package with:

    pip install git@bitbucket.org:3mwdigital/djangocms-dashboard.git

2. Add "djangocms_dashboard" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'djangocms_dashboard',
    ]

3. Include the polls URLconf in your project urls.py like this::

    url(r'^djangocms_dashboard/', include('djangocms_dashboard.urls')),

4. Start the development server and visit http://127.0.0.1:8000/dashboard/
