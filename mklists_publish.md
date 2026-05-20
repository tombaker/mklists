# Publishing mklists in 2026

## What are PyPI and Read the Docs?

**PyPI** (Python Package Index, pypi.org) is the official repository for Python
packages. Publishing to PyPI makes `mklists` installable anywhere with
`pip install mklists` or `pipx install mklists`. It is still the right choice
for distributing a Python CLI tool in 2026 — nothing has displaced it.

**Read the Docs** (readthedocs.io) hosts documentation built from a repository.
It watches the GitHub repo and rebuilds automatically on every push to `main`.
It supports MkDocs (as well as Sphinx). It is free for public/open-source
projects and still widely used. The main alternative is GitHub Pages with a
GitHub Actions workflow, which cuts out the third-party service at the cost of
a little more configuration. Either is a sound choice; Read the Docs requires
less setup if the account and webhook are already in place.

---

## Step 1 — Prepare the main branch

```bash
git checkout main
git merge dev
git push origin main
```

Check that CI (if any) passes on `main` before proceeding.

---

## Step 2 — Bump the version

Edit `pyproject.toml` and set a meaningful version (the current value is
`0.1.0`). Follow [Semantic Versioning](https://semver.org/): given the scope
of recent changes, `0.2.0` is appropriate. Commit the change on `main`
(or merge it from `dev`).

```toml
version = "0.2.0"
```

---

## Step 3 — Rebuild the MkDocs documentation folder

The previous documentation site needs to be re-created from scratch.

### 3a — Install MkDocs

```bash
poetry add --group dev mkdocs mkdocs-material
```

### 3b — Initialise the docs tree

```bash
poetry run mkdocs new .
```

This creates `mkdocs.yml` and `docs/index.md`. Edit `mkdocs.yml` at minimum:

```yaml
site_name: mklists
site_url: https://mklists.readthedocs.io/
repo_url: https://github.com/tombaker/mklists
theme:
  name: material
nav:
  - Home: index.md
  - Usage: usage.md
  - Configuration: configuration.md
  - Rules: rules.md
```

### 3c — Write the documentation pages

At minimum, create the pages referenced in `nav` above inside `docs/`. Draw on
the content of `CLAUDE.md`, `mklists_init.md`, `mklists_symlinks.md`, and the
existing readthedocs pages for what to include.

### 3d — Preview locally

```bash
poetry run mkdocs serve
```

Open `http://127.0.0.1:8000` and review every page before publishing.

### 3e — Add a `.readthedocs.yaml` file

Read the Docs has required this file since 2023; builds will fail without it.
Create it in the repo root:

```yaml
version: 2

build:
  os: ubuntu-24.04
  tools:
    python: "3.14"

mkdocs:
  configuration: mkdocs.yml

python:
  install:
    - requirements: docs/requirements.txt
```

Create `docs/requirements.txt` with at least:

```
mkdocs
mkdocs-material
```

Commit both files.

---

## Step 4 — Reconnect Read the Docs

1. Log in to readthedocs.io and open the `mklists` project.
2. Verify the GitHub webhook is active (Settings → Integrations).
3. Trigger a manual build or push to `main` and confirm the build succeeds.
4. Check https://mklists.readthedocs.io/en/latest/ once the build completes.

---

## Step 5 — Publish to PyPI

### 5a — Configure a PyPI token (once per machine)

Generate an API token at https://pypi.org/manage/account/token/ and store it:

```bash
poetry config pypi-token.pypi pypi-<your-token>
```

### 5b — Build and upload

```bash
poetry publish --build
```

This builds the source distribution and wheel, then uploads both to PyPI.

### 5c — Verify

```bash
pipx install mklists --force
mklists --version
```

Check https://pypi.org/project/mklists/ to confirm the new version appears.

---

## Step 6 — Retire the GitHub Pages site

The old site at https://tombaker.github.io/mklists/ should be disabled to
avoid confusion with two documentation sites. In the GitHub repository settings,
set Pages source to "None" (or leave it — it will simply stop being updated).
Add a redirect or notice if the old URL appears in any external links.

---

## Summary checklist

- [ ] `dev` merged into `main` and pushed
- [ ] Version bumped in `pyproject.toml`
- [ ] MkDocs installed and `docs/` tree written
- [ ] `.readthedocs.yaml` and `docs/requirements.txt` committed
- [ ] Documentation previewed locally with `mkdocs serve`
- [ ] Read the Docs build triggered and verified
- [ ] PyPI token configured
- [ ] `poetry publish --build` run successfully
- [ ] New version visible at pypi.org/project/mklists/
- [ ] GitHub Pages site retired (optional)
