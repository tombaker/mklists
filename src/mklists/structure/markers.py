"""Markers for directory types

Certain marker files, when present, define a directory structurally as a Repo Root
or Datadir:
-  A Repo Root is marked by the presence of `mklists.yaml` and/or `mklists.rules`.
-  A Datadir is marked by the presence of `.rules`.
-  A directory cannot be both a Repo Root and a Datadir.

A Datadir is marked as self-contained if `.mklistsrc` is present. A self-contained
Datadir is processed without reference to repo-level rules or configuration, even if
a Repo Root exists.
"""

DATADIR_CONFIGFILE_NAME = ".mklistsrc"
DATADIR_RULEFILE_NAME = ".rules"
REPO_CONFIGFILE_NAME = "mklists.yaml"
REPO_RULEFILE_NAME = "mklists.rules"
