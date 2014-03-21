class CacheRule(object):
    def __init__(self, **kwargs):
        self.params = kwargs

    def run_rule(self, cache_key):
        pass


class ParametersIgnoreCacheRule(CacheRule):

    def run_rule(self, cache_key):
        for param in self.params.get('parameters'):
            cache_key.cache_components['GET'].pop(param, None)
            cache_key.cache_components['POST'].pop(param, None)


class TruncateParametersCacheRule(CacheRule):

    def run_rule(self, cache_key):
        for key in self.params:
            limit_number = self.params.get(key)
            param = cache_key.cache_components['GET'].get(key, None)
            if param is not None:
                cache_key.cache_components['GET'][key] = param[0][0:limit_number]
            else:
                param = cache_key.cache_components['POST'].get(key, None)
                if param is not None:
                    cache_key.cache_components['POST'][key] = param[0][0:limit_number]


class RoundedFloatParametersCacheRule(CacheRule):

    def run_rule(self, cache_key):
        for key in self.params:
            try:
                rounded_number = self.params.get(key)
                param = cache_key.cache_components['GET'].get(key, None)
                if param is not None:
                    cache_key.cache_components['GET'][key][0] = round(float(param[0]), rounded_number)
                else:
                    param = cache_key.cache_components['POST'][0].get(key, None)
                    param = param[0]
                    if param is not None:
                        cache_key.cache_components['POST'][0][key] = round(float(param[0]), rounded_number)
            except:
                pass # we don't touch a cache component if it errors