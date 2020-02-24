.. _glossary:

Glossary
========

Data directory
    A sub-directory of a repo that contains a hidden rule
    file (`.rules`).

List file
    A disk file in UTF-8 format containing line-oriented
    data (with newlines) and with no blank lines.

List repository (or "repo")
    A directory tree that has been initialized with a
    `mklists` configuration file (`mklists.yml`) and
    global rule file (`rules.cfg`).

Rule file
    A disk file in pipe-delimited CSV format that
    enumerates the rules used to process data lists.
    Aside from using pipe characters (`|`) instead of
    commas, the rule-file format allows values to be
    surrounded with whitespace (which is stripped out
    before processing). The `mklists` program expects a
    "global" rule file (`rules.cfg`) in the root
    directory of the repo and a "local" rule file
    (`.rules`) in each data directory.

Rules
    A list of Rule objects initialized from rule files.

