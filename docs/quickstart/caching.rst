.. _caching:

Caching Your Endpoints
===========================

Once you start getting some traffic, it might make sense to turn on caching to lessen the load from your API backend
services.  Caching API endpoints is subtly different than from caching normal web pages.  Certain parameters can
be ignored (tokens, for instance) if the payload doesn't change based on a token.

Face/Off gives you the functionality to add complex cache rules around each request that can selectively ignore or
truncate parameters as necessary.  For more specific use cases, you can write your own cache rules.

Important Note:  Face/Off always checks authentication before it goes to the cache.

In this example, let's turn on caching and add a simple parameter that will ignore an "access_token" parameter since we
know that if the request passes auth, the results don't change.  Also, let's truncate the "lat", "lng" parameters to
one decimal point, since we don't need extra precision.

.. code-block:: json

    {
        "general": {
            "cache": {
                "ttl": 300,
                "function": "proxy.cache.RedisAPICacheStore",
                "parameters": {
                    "host": "localhost",
                    "port": 6379,
                    "db": 1,
                    "password": ""
                }
            }
        },
        "endpoints": {
            "^api/music/near_me(.*)": {
                "name": "Music Events Near Me Endpoint",
                "auth": false,
                "pass_headers": true,
                "server": {
                    "servers" : [
                        "https://internal1.example.com/music/near/m$1",
                        "https://internal2.example.com/music/near/m$1",
                    ],
                    "rotation_policy": "proxy.rotations.RoundRobin"
                },
                "cache": {
                    "enabled": true,
                    "rules": {
                        "proxy.cache.rules.ParametersIgnoreCacheRule": {
                            "parameters": ["access_token"]
                        },
                        "proxy.cache.rules.TruncateParametersCacheRule": {
                            "lat": 4,
                            "lng": 5
                        }
                    }
                },
                "http_method_names": ["get", "post", "put", "options"],
                "https_only": true
            }
        }
    }

Diving into some specifics:

Cache General Configuration
---------------------------

ttl
```````````
The default ttl is 5 minutes (300 seconds), after that items expire.

function
````````
Face/Off ships with two cache stores.  Above, we are using the `RedisApiCacheStore` which (as you can guess) uses
Redis as the backend store.  We also ship with a very simple `SimpleInMemoryCacheStore` that just uses an
in-memory hash.

parameters
``````````
These are parameters for the specific store.



Cache Endpoint Config
---------------------

You have to actually turn on the cache for an endpoint.  To do this, we specify a `cache` configuration with `enabled`
set to true.  Additionally, we specify the rules we are interested in.

Out of the box, Face/Off has two Cache Rules.  They are found in the `proxy.cache.rules` package:

ParametersIgnoreCacheRule
```````````````````````````````````````````
This takes in a config attribute, `parameters`, which is an array of parameters that will be ignored in a cache.  For instance,
in this case URLs that look exactly the same except for the `access_token` will be cached as the same result.  Note,
this happens *after* auth.

TruncateParametersCacheRule
`````````````````````````````````````````````
This is a simple truncation rule.  It takes in as a parameter, a list of attributes and the amount of characters to
truncate to.
