.. _intro:

Introduction and Installation
=============================

Face/Off is a robust API proxy that takes a request from a client, modify the request's payload, validate
the request's application or consumer keys and then routes it to the appropriate server that can service this request
and can finally modify the response as necessary before returning the client.

A full Face/Off implementation can handle all authentication, health checking and routing of API requests and can
track various analytics of each request.

Python Dependencies
-------------------

Face/Off is built in Python on top of the `Django`_ web framework, but does not require any Django experience.  In fact,
if you are not interested in adding any new functionality or doing any adapter work, no Python knowledge is required
either.

In order to use Face/Off, Python needs to be installed on your system.  It has been tested with Python 2 versions above 2.65.
It has not been tested in Python 3, but it should work.

Sandboxed Installation
----------------------

It is strongly recommended that you use Virtualenv to install Face/Off into a sandboxed Python environment.  Virtualenv
ensures that whatever libraries and dependencies Face/Off needs will only be installed to run Face/Off.  If you plan
on doing any future Python development (or plan on using any other Python projects) this will make sure that you
don't clobber your Face/Off installation with other product library dependencies.

In Mac OS X or Linux, to install Virtualenv, open a terminal and try (Note: this will ask for your password) ::

    $ sudo pip install virtualenv

If this fails try::

    $ sudo easy_install virtualenv

If both fail, try your package manager on Linux or OS X.  For example, in Ubuntu you would try::

    $ sudo apt-get install virtualenv

and if you have `Homebrew`_ install in OS X, try::

    $ brew install virtualenv

If you are on Windows, you can install easy-install and then attempt the easy-install command above without the sudo prefix.

Once you have Virtualenv installed, we can create a sandboxed environment.  To do this, type the commands prefixed with "$"
in the directory you'd like to store your environment::

    $ mkdir faceoff-env
    $ cd faceoff-env
    $ virtualenv env
    New python executable in env/bin/python
    Installing distribute............done.

Now in face-off env, whenever you want to activate this environment, you can do it by typing::

    $ source env/bin/activate

Anything Python related from this point on, in that shell will be localized to your sandbox.

Getting Face/Off from source
----------------------------

Currently Face/Off can not be found in PyPi and must be installed from Git.  To check the code out do the following::

    $ git clone https://github.com/TeamSidewinder/faceoff.git

Installing all Face/Off Dependencies
------------------------------------

Finally, to install all the Face/Off dependencies, we will use pip and the requirements.txt file.::

    $ cd faceoff
    $ pip install -r requirements.txt

Now that you've installed all the dependencies, you are ready to start configuring Face/Off!

Continue with :ref:`configuration`.

.. _Django: https://www.djangoproject.com/
.. _Homebrew: http://mxcl.github.io/homebrew/
