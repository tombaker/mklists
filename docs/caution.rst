Caution
=======

.. warning::

   This program works by destructively rewriting
   line-oriented, UTF-8 encoded lists in one or more
   directories. The program is therefore designed to
   exit with an error message if any anomalies are
   detected.

All :ref:`visible files<Glossary>` in the current working
directory are considered to be "data files" and are
subject to being rewritten. Prior to rewriting, the
program by default backs up all data files to a
time-stamped backup directory. The number of backups
retained can be set to any arbitrary number or to zero
(for "no backups").

Data files:
- Must be encoded as UTF-8.
