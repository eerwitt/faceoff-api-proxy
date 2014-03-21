.. _configuration:

Basic Quick Configuration
=========================

Face/Off configuration is done, by default, in the `faceoff/endpoints.json` file.  In this quick start, we will
start with the simplest configuration possible and then layer on more functionality as needed.

Our Hypothetical Quick-Start Scenario
-------------------------------------

Let's say you'd like to expose a new endpoint that provides full functionality for a RESTful music album endpoint.
This endpoint handles your typical GET, POST, DELETE and PUT methods and returns data back as JSON.  We'd like to configure
Face/Off to proxy between two separate servers (for a form of load balancing) and prohibit all access to the DELETE endpoint.

We want the endpoint's url to look like `https://example.com/api/music/{id}` and our backend api endpoints are
`https://internal[1-3].example.com/internal/a/m/{id}`.  With that being said, let's start with our basic configuration.

Basic endpoints.json configuration
----------------------------------

.. code-block:: json

    {
        "general": {

        },
        "endpoints": {
            "^api/music(.*)": {
                "name": "Music Endpoint",
                "server": {
                    "servers" : [
                        "https://internal1.example.com/internal/a/m$1",
                        "https://internal2.example.com/internal/a/m$1",
                        "https://internal3.example.com/internal/a/m$1"
                    ]
                }
            }
        }
    }

Starting Face/Off
-----------------

With that basic configuration set, we can start Face/Off by going into the faceoff root directory and running::

    $ ./manage.py runserver 8000
    Validating models...

    0 errors found
    May 30, 2013 - 15:22:10
    Django version 1.5, using settings 'faceoff.settings'
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

Once you hit Face/Off the first time at `http://localhost:8000/api/music/1`, you will see it start up::

    2013-05-30 15:25:42,384 [INFO] proxy.faceoff: -------------------------------------------------
    2013-05-30 15:25:42,384 [INFO] proxy.faceoff: Face/Off Version 0.1
    2013-05-30 15:25:42,384 [INFO] proxy.faceoff: I'd like to take his face... off.
    2013-05-30 15:25:42,384 [INFO] proxy.faceoff: -------------------------------------------------
    2013-05-30 15:25:42,384 [WARNING] proxy.faceoff: No domain name in your config, which could cause problems with facaded APIs that need it
    2013-05-30 15:25:42,384 [INFO] proxy.faceoff: Configuring Face/Off with timeout of 0.5
    2013-05-30 15:25:42,384 [WARNING] proxy.faceoff: No application object!  Can't use AppKeyProvider authentication handle
    2013-05-30 15:25:42,384 [INFO] proxy.faceoff: Configuring Face/Off with analytics classes: []
    2013-05-30 15:33:23,939 [WARNING] proxy.faceoff: There is no user provider class, this means Face/Off can't protect endpoints by consumer keys
    2013-05-30 15:25:42,385 [WARNING] proxy.faceoff: You have no healthcheck implementation.  This probably means you have no healthchecks!
    2013-05-30 15:25:42,385 [INFO] proxy.faceoff: Proxy self-check URL is proxy-check
    2013-05-30 15:25:42,385 [INFO] proxy.faceoff: -------------------------------------------------
    2013-05-30 15:25:42,385 [INFO] proxy.faceoff: Face/Off started in 625ms with no errors
    2013-05-30 15:25:42,385 [INFO] proxy.faceoff: -------------------------------------------------

You are now proxying to the destination URLs in your configuration!

Understanding the Startup Messages
----------------------------------

Face/Off uses sensible defaults, but in order to start successfully but in order to have a fully fledged system, we should
handle some of the warnings above.

We'll talk about that and a few other settings next.  Continue with :ref:`extra_config`.