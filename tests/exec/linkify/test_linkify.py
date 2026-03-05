"""Tests $MKLRUN/linkify.py

After all datadir processing passes are complete, 
linkify_datadirs should create a parallel mirror of the datadir tree 
rooted at linkify_dir. 

For each datadir, 
it creates a corresponding subdirectory under linkify_dir. 

For each plain text data file in a datadir, 
it writes a .md file 
in which the lines have wrapped in a single <pre>...</pre> block, 
with any raw URLs in the text converted to <a href="...">...</a> HTML links. 

The result is a set of .md files
that GitHub will render as HTML 
because the <pre> block preserves line structure and whitespace, 
and the inline <a> tags make URLs clickable when viewed on GitHub.

linkify_datadirs:

1. Delete all content under linkify_dir (full shutil.rmtree then recreate), to
   handle renamed/removed datadirs cleanly.
2. For each datadir, create a corresponding subdirectory under linkify_dir,
   mirroring the relative path from config_rootdir.
3. For each visible data file in that datadir, read its full text, pass it
   through _linkify_lines (one <pre> block, URLs converted to <a> tags), and
   write the result to linkify_dir/<rel_path>/<filename>.md.
"""
