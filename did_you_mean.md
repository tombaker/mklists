Validate config file keys and suggest close matches on error

Config files (`mklists.yaml`, `.mklistsrc`) can contain renamed or
misspelled keys that were previously silently ignored during the
default-merge step. This change adds explicit validation so that
unsupported keys cause an immediate, descriptive error rather than
being quietly discarded.

When an unsupported key is found, mklists raises `ConfigError` and
names both the config file and the offending key. When a similar
valid key exists, a "did you mean?" suggestion is appended:

    Config file 'mklists.yaml' contains unsupported key:
    'linkify.linkify_dir'. Did you mean: 'linkify.linkify_md_dir'
    or 'linkify.linkify_html_dir'?

Suggestions are produced by `difflib.get_close_matches` against the
full set of valid dotted-path key names derived from
`DEFAULT_CONFIG_YAML`, so the suggestion set stays in sync with the
schema automatically.

This follows the pattern established by tools such as `cargo` (Rust),
`pre-commit`, and `docker compose`, all of which validate config keys
and surface actionable suggestions rather than silently accepting
unknown settings. `git config`, by contrast, accepts arbitrary keys
without validation and is not a useful model here.

Changes:
- `errors.py`: add `ConfigError`
- `config/resolve.py`: add `_collect_valid_keys` and
  `_check_for_unknown_keys`; call the latter from
  `_load_merged_configdict` after loading the user config dict
- `tests/config/test__check_for_unknown_keys.py`: full test coverage
  for both helpers
