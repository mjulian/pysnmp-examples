pysnmp-examples
===============

poll.py
-------

Polls an F5 load balancer for virtual service connection stats and sends them
to Graphite.


Converting a MIB to Python format
---------------------------------
If you have PySNMP installed, you get the `build-pysnmp-mib` script,
which is simply a wrapper around `smidump` and `libsmi2pysnmp`.

To use: `build-pysnmp-mib -o <output MIB file.py> <MIB file>`

PySNMP doesn't like SNMPv1 MIBs very much, and attempting to convert them will usually
result in file with no Python objects, causing translation errors for your script.

There are two ways around this that I've found:

1) Edit the MIB file to remove all references to a v1 MIB

2) Give up.

Both options suck, I know.
