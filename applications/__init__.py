class _application_cache(object):

    def __init__(self):
        # just for the sake of information
        self.instance = "Instance at %d" % self.__hash__()
        self.cache = {}

    def set(self, key, value):
        self.cache[key] = value

    def delete(self, key):
        del self.cache[key]

    def get(self, key):
        return self.cache.get(key)

    def clear(self):
        self.cache = {}

    def all(self):
        return self.cache.values()

    def keys(self):
        return self.cache.keys()

    def load_from_db(self):
        from applications.models import Application
        self.clear()
        for a in Application.objects.all():  # TODO: Fix this so it doesn't use a hardcoded Application object (and uses one in CFG)
            self.set(a.id, a)


_application_cache = _application_cache()

def application_cache(): return _application_cache
