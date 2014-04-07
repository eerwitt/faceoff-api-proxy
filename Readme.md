Face/off
========
Python Proxy for Django
---------------------------------

Faceoff is a robust proxy written in Python that provides the following functionality:
 - custom authentication in front of endpoints
 - analytics engine
 - health check facilities
 - server rotation policies
 - API versioning (via header)
 - request and response transformers
 - permissions based on http method names

Requirements & Setup
------------
Face/off requires the following:
 - Python (2.6.5+, 2.7)  Note: 3.x is not tested (but should work?), 2.7+ should be installed by default verify your version using: `python --version`
 - Django 1.5+ (This will install w/ the requirements package below.)

First make sure to install `virtualenv` and `pip` via `easy_install`.

```
sudo easy_install virtualenv
sudo easy_install pip
```

Create a virtual environment for faceoff and activate it. Then clone the faceoff code into that environment
```
virtualenv faceoff
cd faceoff
source bin/activate

// Create a code dir to keep the code separate from the virtual environment stuff
mkdir code
cd code
git clone git@github.com:TeamSidewinder/faceoff-api-proxy.git
```

Face/off has additional packages in the `requirements.txt` file, use `pip` to install these packages, (kinda slow).

```
cd faceoff-api-proxy
pip install -r requirements.txt
```

Configuration
-------------
Sweet, now let's configure your database. Open `faceoff/local_settings.py` and you'll notice the `DATABASE` configuration section.
Faceoff should be configured for a MySQL engine, `'ENGINE': 'django.db.backends.mysql'`.
To utilize a different database change the last part of the `ENGINE` string. For certain databases you may have to modify other configuration setttings like, 
`HOST` or `USER`.

For example PostgreSQL might look like
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'faceoff_dev',                    # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'your-user-name',
        'PASSWORD': '',
        'HOST': '127.0.0.1',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                               # Set to empty string for default.
    }
}
```



Migrate the database by running the command:
```
./manage.py syncdb 
```


Starting Face/off
-----------------

####Local proxy

It's as simple as starting `./manage.py runserver`.  By default, after first hit, you should see Face/off logging to the console. 
You should now be up and running. 

####Health check

Start this with the health_check management command: `./manage.py healthcheck ./faceoff/endpoints.json`  You can specify the
frequency if you choose after the file name (default is 60 seconds.) 

####Heroku

There is a procfile that uses gunicorn and gevent's async workers for optimal heroku performance.


Quick Start Endpoint Configuration
----------------------------------
For more details, check out the actual docs (psst, they're not done yet) but for now,
take a look at `endpoints.json`.  A endpoints config has essentially two sections, the `general` section
and the `endpoints` section.

###Conventions

A function/parameters dict is a dict that is of the following format:

```
            "function": "access_tokens.faceoff_auth_provider.LNUserFinder",
            "parameters": {
                "servers": ["http://sleepy-wave-4844.herokuapp.com//user"]
            }
```

where the function can be either a class or function and the parameters are passed in as kwargs.

###General section
Here you can specify the following attributes:

| Setting  | Description | Possible Values    | Default (if any) |  Required  |
|----------|-------------|--------------------|------------------|------------|
| domain_name |  This is the domain that is passed into the `X_FORWARDED_HOST` parameter | sampledomain.com | Uses hostname | False |
| timeout | Timeout waiting for backend service (in seconds) | 1.5 | .5 | False |
| application_object | The application object and service used for Application Auth Provider | `"applications.models.Application"`| None | False |
| user_provider | A function/parameters dict that points to a class that implements `proxy.authentication.UserFinder` | See endpoints.json  | None | False |
| analytics | Is a list of either function/parameter dicts or strings that implement `proxy.analytics.Analytics` for analytic services | `"proxy.analytics.NoOpAnalytics"` | None | False |
| health_check_storage | Health implementation of `proxy.healthchecks.storage.HealthCheckStorage` |  `{ implementation`: `proxy.healthchecks.storage.RedisHealthCheckStorage } `| None | False | 
| self_health_check_url | URL to give status of Face/Off | "^proxy-check$" | "^proxy-check$" | True |

###Endpoint section

| Setting  | Description | Possible Values    | Default (if any) |  Required  |
|----------|-------------|--------------------|------------------|------------|
| url_conf | Actual URL that is being proxied |  `"^users(.*)"` | None | True |
| name | Pretty name for endpoint | `"Users"` | None | True |
| versioning | Should this API be versioned - NOTE NOT IMPLEMENTED YET | true | false | False |
| auth | Should Face/off authenticate this?  This requires an `auth_provider` to be set too | false | false | False |
| auth_provider | The auth provider to use if this is an authenticated endpoint | `"proxy.authentication.appkey_providers.SuperAppKeyProvider"` | None | False |
| pass_headers | Should the request headers be passed in to the response | true | false | False |
| http_method_names | An array of method names Face/off will pass across |  ["get"] | ["get", "post", "options", "delete"] | False |
| transformers | A dict of `response_transformers` and `request_transformers` arrays to transform both side | See endpoints.json | None | False |
| servers | An array of `server` dicts.  See below | See Below | None | True | 

### Server Dicts

| Setting  | Description | Possible Values    | Default (if any) |  Required  |
|----------|-------------|--------------------|------------------|------------|
| servers | array of server names (supporting basic auth, https and regex matching) | ["https://nick:test@nick-test-lnlabs.fwd.wf/users$1"]| None | True
| rotation_policy | how to rotate between servers pointing to an implementation of `proxy.rotations.Rotation` |  | "proxy.rotations.RoundRobin" | False
| health_check | a function/parameter dict for a `proxy.healthchecks.checks.HealthCheck` implementations | | {"function": "proxy.healthchecks.checks.HeadCheck"} | False
| version | version of this endpoint (NOT SUPPORTED YET) | 1 | None | False |

##Auth details

When an authenticated call gets resolved by Face/off, it adds the following headers to the backend server: 
`X-FACEOFF-AUTH`, `X-FACEOFF-AUTH-ID`, `X-FACEOFF-AUTH-JSON`  

Your auth providers are free to add their own.





