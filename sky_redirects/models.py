from django.db import models
from django.contrib.sites.models import Site
from django.core.cache import cache
import re


class RedirectType(object):
    PERMANENT='301'
    TEMPORARY='302'
    CHOICES = (
        (PERMANENT, 'Permanent'),
        (TEMPORARY, 'Temporary')
    )


class IndexedCachedTableManager(models.Manager):
    def __init__(self, indexed_field, *args, **kwargs):
        super(IndexedCachedTableManager, self).__init__(*args, **kwargs)
        self.indexed_field = indexed_field

    def _cache_key(self):
        return '%s:indexed_cached_table' % (self.model.__class__.__name__,)

    def cached_index(self):
        """Returned the cached index, generate it if not present."""
        index = cache.get(self._cache_key())
        if index is None:
            index = self.rebuild_cache()
        return index

    def rebuild_cache(self):
        """Generate the indexed dictionary and publish it to the django cache"""
        index = {}
        for obj in self.all().select_related():
            key = getattr(obj, self.indexed_field, None)
            if key is not None:
                index[key] = obj
        cache.set(self._cache_key(), index, 365*86400)  # cache forever
        return index

class OrderedCachedTableManager(models.Manager):
    def __init__(self, ordering_field, *args, **kwargs):
        super(OrderedCachedTableManager, self).__init__(*args, **kwargs)
        self.ordering_field = ordering_field

    def _cache_key(self):
        return '%s:ordered_cached_table' % (self.model.__class__.__name__,)

    def cached_index(self):
        """Returned the cached index, generate it if not present."""
        index = cache.get(self._cache_key())
        if index is None:
            index = self.rebuild_cache()
        return index

    def rebuild_cache(self):
        index = []
        for obj in self.all().order_by(self.ordering_field):
            index.append(obj)
        cache.set(self._cache_key(), index, 365*86400) # cache forever
        return index



class CachedTable(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        ret = super(CachedTable, self).save(*args, **kwargs)
        #anytime after we change a record, update the cached_index
        self.__class__.objects.rebuild_cache()
        return ret



class DomainRedirect(CachedTable):
    domain = models.CharField(max_length=1024, null=False, help_text='The domain to redirect from.  You may terminate the domain with a `.` to specify a subdomain e.g.: `www.`')
    redirect_to = models.ForeignKey('sites.Site')
    redirect_type = models.CharField(max_length=1024, choices=RedirectType.CHOICES, default=RedirectType.PERMANENT)
    objects = IndexedCachedTableManager(indexed_field='fqdn')

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

class RegexPathRedirect(CachedTable):
    redirect_from = models.CharField(max_length=1024, help_text='Regular Expression format, remember to include `$` if you want an exact match' )
    redirect_to = models.CharField(max_length=1024)
    redirect_type = models.CharField(max_length=1024, choices=RedirectType.CHOICES, default=RedirectType.PERMANENT)
    ordering = models.IntegerField(default=99, choices=((c,c) for c in range(1,100)))
    objects = OrderedCachedTableManager(ordering_field='ordering')

    class Meta:
        ordering = ('ordering',)

    def __unicode__(self):
        return "Redirect from '%s' to '%s'" % (self.redirect_from, self.redirect_to)

    def save(self, *args, **kwargs):
        self.redirect_from = self.redirect_from.strip()
        self.redirect_to = self.redirect_to.strip()
        return super(RegexPathRedirect, self).save(*args, **kwargs)

    @property
    def compiled_regex(self):
        return re.compile(self.redirect_from)





