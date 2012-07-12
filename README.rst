
Usage
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