=======
Clients
=======
OpenCAFE strives to provide a standard way of interacting with as many
technologies as possible, in order to make functional testing of highly
integrated systems easy to write, manage, and understand.
Clients provide easy interaction with myriad technologies via foreign function
interfaces for RESTfull APIs, command line tools, databases and the like.

Design
------

* Clients should be simple and focused on providing native access to foreign
functionality in a clean and easy to understand way.

* A client should not make assumptions about how it will be used, beyond
those mandated by the foreign functionality.

* A client should be able to stand on it's own, without requiring any
configuration or information beyond what is required for instantiation.

Examples
--------

 * The HTTP client itself doesn't require any information to instantiate,
but an API client built using the HTTP client might require a URL and an auth
token, since it's purpose is to interact solely with the API located at that
URL.

 * The commandline client offers logging, a uniform request/response model, and
both synchronous and asynchronous requests on top of python's Popen method,
but doesn't seek to expose functionality beyond running cli commands. The
client deals with Popen and provides a simple way to get stdout, stderr, and
stdin from a single command send to the local commandline. The client itself
can be instantiated with a base command and used as an ad hoc interface for a
specific commandline program, or left without a base command and used as an
interface for the underlying shell.