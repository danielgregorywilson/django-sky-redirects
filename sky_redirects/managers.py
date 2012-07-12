from django.db import models
from django.core.cache import cache

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

