Robust redirect app for Django that supports domain redirects and regular expression patterns. Set up and edit redirects using domains or regular expressions from the Django admin site, order by priority, and flag as temporary or permanent. Use it to preserve legacy URLs or to add extra slugs or short URLs to a single page.

Setup
=====

add 'sky_redirects' to INSTALLED_APPS in settings.py::

   INSTALLED_APPS = (
      'sky_redirects',
      ...

Add the sky_redirects middleware to the *beginning* of MIDDLEWARE_CLASSES in settings.py::

   MIDDLEWARE_CLASSES = [
      'sky_redirects.middleware.DomainRedirectMiddleware',
      'sky_redirects.middleware.RegexRedirectMiddleware',
      ...

Then run syncdb, and you are ready to go!