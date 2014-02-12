=======
Clients
=======
OpenCafe strives to provide a standard way of interacting with as many
technologies as possible, in order to make functional testing of highly
integrated systems easy to write, manage, and understand.
Clients provide easy interaction with myriad technologies via foreign function
interfaces for RESTfull API's, command line tools, databases and the like.

Design
------

Clients should be narrowly-focused and simple, one client per api for example.
They should try to not make any assumptions about how a user will use them,
and should instead try to provide native access to as much of the foreign
functionality as is possible in a clean and easy to understand way.

