.. _user_auth:

Adding Application Validation and User Authentication
=====================================================

Finally, let's protect our endpoint so that only users with valid access tokens can access the API endpoint.

We'll add some configuration to accomplish this to our endpoints.json.  This is how our config will look.

.. code-block:: json

    {
        "general": {
            "domain_name": "faceoff-demo-1234.herokuapp.com",
            "timeout": "1.5",
            "application_object": "applications.models.Application",
            "user_provider": {
                "function": "proxy.authentication.user_finders.MockUserFinder"
            },
            "analytics":
                [
                    "proxy.analytics.NoOpAnalytics",
                    {
                        "function": "proxy.analytics.StatsDAnalytics",
                        "parameters": {
                            "host": "localhost",
                            "port": 8125,
                        }
                    }
                ],
            "health_check_storage" : {
                "implementation": "proxy.healthchecks.storage.RedisHealthCheckStorage",
                "redis": {
                    "use_settings" : true,
                    "host": "localhost",
                    "port": 6379,
                    "db": 0,
                    "password": ""
                }
            },
            "self_health_check_url": "^proxy-check$"
        },
        "endpoints": {
            "^api/music(.*)": {
                "name": "Music Endpoint",
                "auth": true,
                "auth_provider": "proxy.authentication.app_key_providers.AppKeyProvider",
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
                "https_only": true,
                "transformers": {
                    "response_transformers": ["proxy.transformers.XMLTOJSONTransformer"]
                }
            }
        }
    }

Basic Authentication
--------------------

In order for Face/Off to handle authentication for your application, you will need to integrate your application
with Face/Off.  Generally, a lot of code here is often custom for your environment so please take a look at the sample
code for some implementations (TODO: THERE IS NO SAMPLE CODE - IT'S LN ENV CODE.)

application_object
``````````````````
Face/Off expects that protected endpoints are at least tied to an `Application`.  The simplest secure application
implementation expects a client-id passed in that maps to an Application inside Face/Off.  The Application object
used in this example code is a very simple database model that contains a name, id, and owner.

user_provider
`````````````
If you'd like to add Users as well (so the API is authenticated by not just an application, but also a User), a
`user_provider` implementation needs to be created.  This built-in mock implementation returns the same user.


auth_provider
`````````````
Each endpoint could be secured by different auth_provider implementations.  The simple Provider above just
verifies that the Application object (from applications.model.Application) for the client-id exists.

What is Passed to the API Endpoints
-----------------------------------

Face/Off handles the actual authentication and mapping of Client-Ids and Application-Ids.  Your backend servers
do not need to worry about this and can trust Face/Off's response.

Face/Off returns back information about the user and application via extra custom headers your API can utilize.  The
headers typically look like::

    X-FACEOFF-AUTH: Face/Off App Key Provider
    X-FACEOFF-AUTH-USER-ID: 42
    X-FACEOFF-AUTH-APP-ID: 31337


    X-FACEOFF-AUTH-APP: {"id": 31337, "name": "Super App", "owner": "Nick Vlku"}
    X-FACEOFF-AUTH-USER: {"id": 42, "full name": "Zipper Vlku", "animal": "cat"}

Keep in mind, the actual values for many of these headers will be custom to your environment (for instance, the User
above.)

Now with traffic, you might start to need caching.  Fortunately, Face/Off provides caching functionality as well.

Continue with :ref:`caching`.


