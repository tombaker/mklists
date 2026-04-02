# Linkify: generating browsable copies of your data files

`mklists linkify` mirrors every data directory as a tree of files with URLs
converted to clickable links. Each visible data file is written as a copy
wrapped in a `<pre>` block with every `http://` or `https://` URL replaced
by an HTML `<a>` tag.

## The extension problem

The file extension determines where the output is usable:

| Extension | GitHub | Dropbox |
|-----------|--------|---------|
| `.md`     | clickable links (GitHub renders Markdown and passes through `<pre>` and `<a>` tags) | raw text — tags visible as literal markup, links not clickable |
| `.html`   | raw text — GitHub displays HTML files as source code | clickable links (any web server that serves `.html` files, including Dropbox) |

There is no single extension that works for both platforms.

## Generating output for both platforms

`mklists.yaml` supports two independent linkify targets:

```yaml
linkify:
  linkify_enabled: True
  linkify_dir: .linkify          # writes <filename>.md  — for GitHub
  linkify_html_dir: .linkify_html  # writes <filename>.html — for Dropbox
```

Either or both targets can be enabled independently:

- Set `linkify_dir` to generate `.md` files (GitHub).
- Set `linkify_html_dir` to generate `.html` files (Dropbox).
- Set both to generate output for both platforms in one run.

Both directories are wiped and rebuilt from scratch on every run.

## Choosing what you need

- **GitHub only** — use `linkify_dir`; leave `linkify_html_dir` unset.
- **Web server only** (including Dropbox) — use `linkify_html_dir`; leave `linkify_dir` unset.
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
