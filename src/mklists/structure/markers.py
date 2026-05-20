"""Markers for directory types

Certain marker files, when present, define a directory structurally as a Datatree
root or Datadir:
-  A Datatree root is marked by the presence of `mklists.yaml` and/or `mklists.rules`.
-  A Datadir is marked by the presence of `.rules`.
-  A directory cannot be both a Datatree root and a Datadir.

A Datadir is marked as self-contained if `.mklistsrc` is present. A self-contained
Datadir is processed without reference to datatree-level rules or configuration, even
if a Datatree root exists.
"""

DATADIR_CONFIGFILE_NAME = ".mklistsrc"
DATADIR_RULEFILE_NAME = ".rules"
DATATREE_CONFIGFILE_NAME = "mklists.yaml"
DATATREE_RULEFILE_NAME = "mklists.rules"
