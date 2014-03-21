.. Face/off documentation master file, created by
   sphinx-quickstart on Wed May 29 11:32:15 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Face/Off:  A Proxy for APIs and Stuff
=====================================

Face/Off provides functionality for proxying API requests to multiple back end servers.

Features
--------
Face/Off is intended as a full API proxy with robust features, including:

- Proxying endpoints to multiple backend servers (using Regex for more finely grained forwarding.)
- Health checks against endpoints (including the ability to do custom healthchecks)
- Passing across custom authentication credentials to endpoints (and securing them)
- Request and response transformers
- Statistics gathering with custom adapters (StatsD adapter included)
- Can forward to Basic Auth protected endpoints
- Caching layer with custom store implementations and rules (Redis store included)
- Versioning *[planned]*


Quickstart
----------
Here we run through a sample configuration that covers the major functionality of Face/Off.

.. toctree::
   :maxdepth: 2

   quickstart/intro_installation
   quickstart/configuration
   quickstart/extra_config
   quickstart/health_checks_and_status
   quickstart/user_auth
   quickstart/caching

Details
-------
Some more detailed discussion of the various modules in Face/Off,
the standard ones included in Face/Off and how you can implement your own.

.. toctree::
   :maxdepth: 2

   modules/life_cycle
   modules/endpoints
   modules/health_check
   modules/request_response_transformers
   modules/analytics
   modules/application_auth
   modules/user_auth
   modules/management_commands
   modules/integrating_your_api_with_faceoff

Code Documentation
------------------
Specific information about documentation from the code.

.. toctree::
   :maxdepth: 2

   code_documentation


Raw Code Index and Documentation
--------------------------------

.. toctree::
   :maxdepth: 3

   code/modules


Contact Info
------------

Face/Off was developed by Nick Vlku at LiveNationLabs, a technical lab unit of LiveNation.

