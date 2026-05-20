# Linkify

`exec/linkify.py` mirrors every datadir as a tree of files with URLs converted to
clickable `<a>` tags. Each file is wrapped in a single `<pre>` block.

Two output formats are supported, controlled by separate keys in `mklists.yaml`
or `.mklistsrc`:

```yaml
linkify:
  linkify_md_dir: null   # set to a name or absolute path to enable
  linkify_html_dir: null
```

- **`linkify_md_dir`** — writes `<filename>.md` (HTML-in-Markdown). GitHub renders
  `.md` files and passes through `<pre>` and `<a>` tags, so links are clickable when
  browsing the repository. A `.html` extension would cause GitHub to show raw source
  instead.

- **`linkify_html_dir`** — writes `<filename>.html`. Any web server (including
  Dropbox) serves `.html` as rendered HTML with clickable links.

Either or both can be set independently. The output directory is wiped and rebuilt
from scratch on every run, so stale files from previous runs are never left behind.

## Example

A data line such as:

```
See https://example.com for details.
```

becomes:

```html
<pre>
See <a href="https://example.com">https://example.com</a> for details.
</pre>
```

## Known limitation

Trailing punctuation characters (`.`, `,`, `;`, `:`, `!`, `)`, `?`) are detected and
moved outside the `<a>` tag so they are not included in the link target. URLs that
genuinely end with one of those characters (rare) will have that character incorrectly
stripped.
