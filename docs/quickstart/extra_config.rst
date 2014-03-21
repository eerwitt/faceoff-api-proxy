.. _extra_config:

Extra Configuration Options
===========================

In our next stab at the configuration, we will add some overrides for default behaviors and lock down the endpoint
so that only some HTTP methods can get to it.  We're also going to more specifically call out some defaults.

.. code-block:: json

    {
        "general": {
            "domain_name": "faceoff-demo-1234.herokuapp.com",
            "timeout": "1.5"
        },
        "endpoints": {
            "^api/music(.*)": {
                "name": "Music Endpoint",
                "auth": false,
                "pass_headers": true,
                "server": {
                    "servers" : [
                        "https://internal1.example.com/internal/a/m$1",
                        "https://internal2.example.com/internal/a/m$1",
                        "https://internal3.example.com/internal/a/m$1"
                    ],
                    "rotation_policy": "proxy.rotations.RoundRobin"
                },
                "http_method_names": ["get", "post", "put", "options"],
                "https_only": true
            }
        }
    }

And let's start and hit the endpoint url again::

    2013-05-30 15:39:55,397 [INFO] proxy.faceoff: -------------------------------------------------
    2013-05-30 15:39:55,397 [INFO] proxy.faceoff: Face/Off Version 0.1
    2013-05-30 15:39:55,397 [INFO] proxy.faceoff: I'd like to take his face... off.
    2013-05-30 15:39:55,397 [INFO] proxy.faceoff: -------------------------------------------------
    2013-05-30 15:39:55,397 [INFO] proxy.faceoff: Configuring Face/Off with domain name: faceoff-demo-1234.herokuapp.com, Overrode from FACEOFF_DOMAIN_NAME env variable: False
    2013-05-30 15:39:55,397 [INFO] proxy.faceoff: Configuring Face/Off with timeout of 1.5
    2013-05-30 15:39:55,397 [WARNING] proxy.faceoff: No application object!  Can't use AppKeyProvider authentication handle
    2013-05-30 15:39:55,397 [INFO] proxy.faceoff: Configuring Face/Off with analytics classes: []
    2013-05-30 15:39:55,397 [WARNING] proxy.faceoff: There is no user provider class, this means Face/Off can't protect endpoints by consumer keys
    2013-05-30 15:39:55,397 [WARNING] proxy.faceoff: You have no healthcheck implementation.  This probably means you have no healthchecks!
    2013-05-30 15:39:55,397 [INFO] proxy.faceoff: Proxy self-check URL is proxy-check
    2013-05-30 15:39:55,397 [INFO] proxy.faceoff: -------------------------------------------------
    2013-05-30 15:39:55,397 [INFO] proxy.faceoff: Face/Off started in 677ms with no errors
    2013-05-30 15:39:55,397 [INFO] proxy.faceoff: -------------------------------------------------

So what did we do?

Basic Overrides and General Configs
-----------------------------------

domain_name
```````````
The general endpoint has many configuration options that are discussed in detail at :ref:`endpoints`.  Here we added two
parameters, the first is a `domain_name` setting.  With this settings, Face/Off will pass along it's own domain name
as a special header to the your backend servers.  This can then be used by your APIs to rewrite urls relative to Face/Off,
if needed.  The header is `X_FORWARDED_HOST`.

timeout
```````
By default, Face/Off well time out a connection to a destination endpoint if it doesn't respond with .5 seconds.  If your
endpoint takes longer, this could be customized.  Be warned, if you make this setting to high, you'll increase the load
on the Face/Off proxy server.

Endpoint Overrides
------------------

Endpoints have many configuration options, we've added a few here.  They include

auth
````
By default, the authorization layer is disabled.  We've explicitly turned it off here.  We'll talk about turning it on
in the next few sections.

pass_headers
````````````
By default, Face/Off will pass the exact headers from the client to the backend endpoint except for the Hostname header.
If you'd like Face/Off to completely wipe the headers before sending them to your endpoint, set this value to false.

rotation_policy
```````````````
Face/Off lets you specify your own server rotation policy, if you have the ability to do some custom logic to make
your rotation smarter.  By default, it uses the included RoundRobin policy.

http_method_names
`````````````````
By default, Face/Off will allow all HTTP methods across to the endpoint.  We can use this option to restrict some.
In this case, we removed the DELETE header from the allowed headers.  (Future feature request for different rules/routes
for different methods is in the planned work.)

https_only
``````````
Face/Off can make sure that API endpoints are only accessible via HTTPS.  This detection/restriction works with both
native SSL servers or Heroku SSL endpoints.  Here, we set it to true to enforce this.  (Note this will not work in
local development.)

Now that this is done, we will enable health checks and turn them on.

Continue on to :ref:`health_checks_and_status`.