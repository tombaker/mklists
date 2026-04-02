# Linkify: generating browsable copies of your data files

`mklists linkify` mirrors every data directory as a tree of files with URLs
converted to clickable links. Each visible data file is written as a copy
wrapped in a `<pre>` block with every `http://` or `https://` URL replaced
by an HTML `<a>` tag.

## The extension problem

The file extension determines where the output is usable:

| Config key / extension | GitHub | Any web server (e.g. Dropbox) |
|------------------------|--------|-------------------------------|
| `linkify_md_dir` / `.md` | clickable links — GitHub renders Markdown and passes through `<pre>` and `<a>` tags | raw text — tags appear as literal markup |
| `linkify_html_dir` / `.html` | raw text — GitHub displays `.html` files as source code | clickable links — served as rendered HTML |

There is no single extension that works for both platforms.

## Generating output for both platforms

`mklists.yaml` supports two independent linkify targets:

```yaml
linkify:
  linkify_md_dir: .linkify          # writes <filename>.md  — for GitHub
  linkify_html_dir: .linkify_html   # writes <filename>.html — for any web server
```

Either or both targets can be enabled independently by setting a path (relative
or absolute); `null` disables that output.

Both directories are wiped and rebuilt from scratch on every run.

## Choosing what you need

- **GitHub only** — set `linkify_md_dir`; leave `linkify_html_dir: null`.
- **Web server only** (including Dropbox) — set `linkify_html_dir`; leave `linkify_md_dir: null`.
- **Both** — set both to cover GitHub and any web server in one run; the extra cost per run is negligible.

## Known limitation

Trailing punctuation characters (`.,;:!?)`) are stripped from the end of
detected URLs and placed after the closing `</a>` tag, so they are not
included in the link target. This is the right behaviour for prose such as:

```
See https://example.com for details.
```

but will incorrectly strip a trailing character from URLs that genuinely end
with one of those characters, for example:

```
https://en.wikipedia.org/wiki/DOT_(graph_description_language)
```
