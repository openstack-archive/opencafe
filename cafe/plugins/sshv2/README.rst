Notes about installation
========================

The sshv2 plugin requires Paramiko, which in the past relied on the pycrypto
library.
As of  Paramiko v2.0, the pycrypto library has been replaces with the
Python Cryptographic Authority's cryptography library.  While this is a good
change overall, some systems may be lacking the required libraries.

This plugin will continue to use 1.17.0 for the near term, but will eventually
switch to paramiko > 2, at which point it will be neccessary for users to
upgrade their systems in order to install this plugin.

For information about the transition from 1.17.0 to 2.0 and the involved
changes, please see http://www.paramiko.org/changelog.html
