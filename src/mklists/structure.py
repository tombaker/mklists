"""Marker filenames for Repo Roots and Datadirs

A directory may be defined structurally as a Repo Root or a Datadir: 
-  A Repo Root is marked by the presence of `mklists.yaml` and/or `mklists.rules`.
-  A Datadir is marked by the presence of `.rules`.
-  A directory cannot be both a Repo Root and a Datadir.

A Datadir may be marked as "self-contained" by the presence of `.mklistsrc`. It is
processed without reference to any rules or config settings defined in a Repo Root, 
even if one exists.
"""

DATADIR_CONFIGFILE_NAME = ".mklistsrc"
DATADIR_RULEFILE_NAME = ".rules"
REPO_CONFIGFILE_NAME = "mklists.yaml"
REPO_RULEFILE_NAME = "mklists.rules"
