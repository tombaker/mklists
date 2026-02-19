"""Structural constants defining repository and datadir markers.

Resolution of run contexts

In Mklists, a directory is interpreted structurally as either a Repo Root
or a Datadir. A Repo Root is defined by the presence of `mklists.yaml`
and/or `mklists.rules`; a Datadir is defined by the presence of `.rules`.
A directory may not be both.

Configuration files (`mklists.yaml` or `.mklistsrc`) define global
execution context and are directly relevant to processing the directory
in which they are found. Rule files, however, are applied only when
processing a Datadir. A Repo Root is not itself processed as a Datadir;
instead, it serves as an orchestration point from which Datadirs are
discovered and processed individually. For this reason, the RunContext
for a Repo Root never includes rule_files, even if `mklists.rules`
exists in that directory.

Datadirs may inherit configuration and rule files only from their
immediate parent Repo Root unless they contain `.mklistsrc`, which
makes them self-contained and prevents inheritance.
"""

DATADIR_CONFIGFILE_NAME = ".mklistsrc"
DATADIR_RULEFILE_NAME = ".rules"
REPO_CONFIGFILE_NAME = "mklists.yaml"
REPO_RULEFILE_NAME = "mklists.rules"
