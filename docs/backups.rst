Automatic backups
=================

Mklists initializes an in-memory dictionary with the concatenated contents of all files in a given data directory, processes their contents in memory, and writes new data files back to disk.  Mklists is designed to exit with helpful error messages if that directory is found to contain anything that does not look like line-oriented lists data in plain text, such as ZIP files, editor-specific temporary files, or binaries.  It tries hard to anticipate, and guard against, the most common causes of corrupted or garbled data.

Before writing the new data files to disk, Mklists (by default) moves the existing data files to a backup directory.  The backup directory can be useful as a reference if the resulting files are not structured or composed as expected.  For example, if a system log -- in plain text with no blank lines -- were somehow copied to the directory before running Mklists, it would unhelpfully be merged into, and processed along with, the intended data.  In such cases, the backup provides an easily accessible snapshot of the directory before processing that can be used to diagnose errors.

The number of backups retained by Mklists can be adjusted by editing the `backup_depth` option in the configuration file, `mklists.yml`.

If backups are not required (for example, the lists are under another form of version control such as `git`), backups can be turned off entirely by setting the `backup_depth` to zero.
