```
Usage: mklists status [OPTIONS]

  Show current directory's mklists structural context and configuration.

Options:
  -C PATH  Show status as if run in PATH instead of CWD.
  --help   Show this message and exit.

Date: 2026-05-20
```

Example output when run from within a datadir:
```
Directory : /Users/tombaker/agendas/agenda
Role      : datadir (in datatree)
Datadirs  : agenda in scope

Datatree marker/config files:
  mklists.yaml  : /Users/tombaker/agendas/mklists.yaml
  mklists.rules : /Users/tombaker/agendas/mklists.rules

Datadir marker/config files:
  .rules        : /Users/tombaker/agendas/agenda/.rules
  .mklistsrc    : not found

Config:
  Config file      : /Users/tombaker/agendas/mklists.yaml
  Backup dir       : /Users/tombaker/Dropbox/agendas_backup
  Linkify MD dir   : /Users/tombaker/Dropbox/agendas_md
  Linkify HTML dir : /Users/tombaker/Dropbox/agendas_html
```

Example output when run from root directory of a datatree:
```
Directory : /Users/tombaker/agendas
Role      : datatree root
Datadirs  : agenda, handles, logs, phone in scope

Datatree marker/config files:
  mklists.yaml  : /Users/tombaker/agendas/mklists.yaml
  mklists.rules : /Users/tombaker/agendas/mklists.rules

Datadir marker/config files:
  .rules        : not found
  .mklistsrc    : not found

Config:
  Config file      : /Users/tombaker/agendas/mklists.yaml
  Backup dir       : /Users/tombaker/Dropbox/agendas_backup
  Linkify MD dir   : /Users/tombaker/Dropbox/agendas_md
  Linkify HTML dir : /Users/tombaker/Dropbox/agendas_html
```
