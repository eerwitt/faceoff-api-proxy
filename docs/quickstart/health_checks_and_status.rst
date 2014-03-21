.. _health_checks_and_status:

Adding Health Checks, Analytics and Tying It All Off
====================================================

Now that we have our service up and running, let's make sure it stays up with health checks.  Additionally,
let's pretend the backend API returns XML and we want Face/Off to convert the response to JSON.  Finally, let's add
analytics so we can see how often our APIs get hit.

After all this is done, our JSON config should look like:

.. code-block:: json

    {
        "general": {
            "domain_name": "faceoff-demo-1234.herokuapp.com",
            "timeout": "1.5",
            "health_check_storage" : {
                "implementation": "proxy.healthchecks.storage.RedisHealthCheckStorage",
                "redis": {
                    "use_settings" : false,
                    "host": "localhost",
                    "port": 6379,
                    "db": 0,
                    "password": ""
                }
            },
            "self_health_check_url": "^proxy-check$",
            "analytics": [
                    "proxy.analytics.NoOpAnalytics",
                    {
                        "function": "proxy.analytics.StatsDAnalytics",
                        "parameters": {
                            "host": "localhost",
                            "port": 8125
                        }
                    }
            ]
        },
        "endpoints": {
            "^api/music(.*)": {
                "name": "Music Endpoint",
                "auth": false,
                "pass_headers": true,
                "server": {
                    "health_check": {
                        "function": "proxy.healthchecks.checks.HeadCheck"
                    },
                    "servers" : [
                        "https://internal1.example.com/internal/a/m$1",
                        "https://internal2.example.com/internal/a/m$1",
                        "https://internal3.example.com/internal/a/m$1"
                    ],
                    "rotation_policy": "proxy.rotations.RoundRobin"
                },
                "http_method_names": ["get", "post", "put", "options"],
                "https_only": true,
                "transformers": {
                    "response_transformers": ["proxy.transformers.XMLToJSONTransformer"]
                }
            }
        }
    }

Health Check Additions
----------------------

health_check_storage
````````````````````
In the general section, we added a `health_check_storage` section.  In this section, we specified the built-in
:class:`proxy.healthchecks.storage.RedisHealthCheckStorage` implementation.  If you'd like to build your own,
you can extend :class:`proxy.healthchecks.storage.HealthCheckStorage`.

self_health_check_url
`````````````````````
We've also added a `self_health_check_url` configuration option.  This will map a url at that location (in the above
example it would be at https://faceoff-demo-1234.herokuapp.com/proxy-check ) that gives you status information about
the various endpoints.  That url can also take a ?details=true parameter to give you detailed information about
each endpoints' server status.

health_check
````````````
In the actual endpoint configuration, we've specified that we'd like to use the built-in
:class:`proxy.healthchecks.checks.HeadCheck` health check which does a simple HEAD request against the endpoint.


Analytics Additions
-------------------

analytics
`````````
The general `analytics` section lets you chain multiple analytic store implementations.  In this example we are using
the Logger only :class:`proxy.analytics.NoOpAnalytics` implementation and the :class:`proxy.analytics.StatsDAnalytics`
implementation that takes a few parameters.  If you are writing your own Analytics solution, you can write your own adapter
(which can take arbitrary parameters) by implementing :class:`proxy.analytics.Analytics`.

Transformer Additions
---------------------

response_transformers
`````````````````````
Face/Off's lifecycle gives you the opportunity to modify both the client request before it gets to your endpoint
and API response before it is sent back.

Please see :ref:`lifecycle` for more details on where these processes run.
In this case, we've added a XMLToJSONTransformer that will take the API's XML response and turn it into JSON.


Turning On The Health Check
===========================

The health check's run as a separate out of band process (and can be run on any server, not just the proxying server).

To run the health check, from the Face/Off root directory, run::

    $ ./manage.py healthcheck ./faceoff/endpoints.json 10

    [...faceoff startup snipped...]

    2013-05-31 14:28:55,596 [INFO] proxy.management.commands.healthcheck: Health Check for Music Endpoint, servers: [u'https://internal1.example.com/internal/a/m$1', u'https://internal2.example.com/internal/a/m$1', u'https://internal3.example.com/internal/a/m$1'], function: proxy.healthchecks.checks.HeadCheck

    2013-05-31 14:28:55,613 [WARNING] proxy.management.commands.healthcheck: SERVICE IS DOWN Healthcheck Result: Music Endpoint: [u'Music Endpoint:https://internal1.example.com/internal/a/m:False', u'Music Endpoint:https://internal2.example.com/internal/a/m:False', u'Music Endpoint:https://internal3.example.com/internal/a/m:False']


The `healthcheck` command asks for a Face/Off configuration file (so you can run many health checks from "health check" server)
and a frequency parameter in seconds (the default is 60 seconds.)

Once your Face/Off health checks are running, you can hit the proxy-check URL to see the status of your endpoints.

Finally, let's tie this all together with Application and User authentication.

Continue with :ref:`user_auth`.


