.. _code-documentation:

Here you will find detailed information on various stores and transformers.  If you are interested in writing your own
implementations of some Face/Off internals, this is the place to get more info (along with the actual code!)

Store Details
=============

If you are interested in implementing your own stores, here are the base requirements for each (and the implementations
that already exist in Face/Off)

Analytics
---------

.. automodule:: proxy.analytics
    :members:
    :show-inheritance:

Health check
------------

.. automodule:: proxy.healthchecks.storage
    :members:
    :show-inheritance:


Health Check Details
====================

If you'd like to write your own health check, here are the docs for that.  (Also, the documentation for currently
available health checks.)

.. automodule:: proxy.healthchecks.checks
    :members:
    :show-inheritance:


Transformers
============

Face/Off lets you write transformers that can modify the request or response from both the client and the endpoint.
See the :ref:`lifecycle` for more details on where these transformers run.

.. automodule:: proxy.transformers
    :members:
    :show-inheritance:

