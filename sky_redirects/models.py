from django.db import models
from django.contrib.sites.models import Site

from django.core.cache import cache



class DomainRedirectManager(models.Manager):
    def _index_cache_key(self):
        return '%s:cached_by_domain' % (self.model.__class__.__name__,)

    def cached_index(self):
        """Index the entire DomainRedirect table into a dictionary of domains to model objects"""
        cache_key = self._index_cache_key()
        index = cache.get(cache_key)
        if index is None:
            index = self.rebuild_cache(cache_key)
        return index

    def rebuild_cache(self, cache_key=None):
        """Publish """
        index = {}
        for domain_redirect in self.all().select_related():
            index[domain_redirect.fqdn] = domain_redirect
        if cache_key is None:
            cache_key = self._index_cache_key()
        cache.set(cache_key, index, 365*86400)  # cache forever
        return index



class DomainRedirect(models.Model):
    REDIRECT_TYPE_PERMANENT='301'
    REDIRECT_TYPE_TEMPORARY='302'
    REDIRECT_TYPE_CHOICES = (
        (REDIRECT_TYPE_PERMANENT, 'Permanent'),
        (REDIRECT_TYPE_TEMPORARY, 'Temporary')
    )
    domain = models.CharField(max_length=1024, null=False, help_text='The domain to redirect from.  You may terminate the domain with a `.` to specify a subdomain e.g.: `www.`')
    redirect_to = models.ForeignKey('sites.Site')
    redirect_type = models.CharField(max_length=1024, choices=REDIRECT_TYPE_CHOICES, default=REDIRECT_TYPE_PERMANENT)
    objects = DomainRedirectManager()

    def __unicode__(self):
        return '%s Redirect from:\'%s\' to \'%s\'' % (self.get_redirect_type_display(), self.fqdn, self.redirect_to.domain)

    @property
    def fqdn(self):
        if self.domain.endswith('.'):
            return '%s%s' % (self.domain, self.redirect_to.domain)
        return self.domain



    def save(self, *args, **kwargs):
        ret = super(DomainRedirect, self).save(*args, **kwargs)
        #anytime after we change a record, update the cached_index
        DomainRedirect.objects.rebuild_cache()
        return ret