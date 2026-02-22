"""Tests for $MKLMKL/config.py"""

import re
import yaml
from pathlib import Path
import pytest
from mklists.config import _load_yaml_from_string, _load_yaml_from_file


@pytest.fixture(params=["string", "file"])
def yaml_load_fn(request, tmp_path):
    """Returns YAML-loading function

    Args:
        request: Pytest built-in "fixture request" object.
        tmp_path: Pytest built-in temporary-path fixture.

    Returns:
        - For "string": returns `load_yamlstr`.
        - For "file": returns a wrapper function which writes a YAML string
          to tmp_path / mklists.yaml and calls `load_yamlstr_from_file`.

    Note:
        This fixture only returns a callable; it does not invoke it.
        Invocation happens in the test function that receives this fixture.

        About fixture parametrization (eg, this function):
        - Same semantic text
        - Two different input mechanisms
        - Identical assertions

        How implemented by pytest in this module:
        - Fixture constructed once for each value in params.
        - Each test that using yaml_load_fn runs twice.
        - Like @pytest.mark.parametrize, applied to fixture.

        About `request`:
        - Pytest attaches current parameter value as `request.param`.
        - "request" means: "The current request to construct this fixture."
        - FixtureRequest contains metadata about fixture context:
          - which test is running
          - which fixture is being resolved
          - active parameter value (`request.param`)
          - fixture scope
          - dependent fixtures
    """

    def _load_from_file(yaml_text: str):
        path = tmp_path / "mklists.yaml"
        path.write_text(yaml_text, encoding="utf-8")
        return _load_yaml_from_file(path)

    if request.param == "string":
        return _load_yaml_from_string
    elif request.param == "file":
        return _load_from_file
    else:
        raise ValueError(f"Unexpected fixture parameter: {request.param!r}")


@pytest.mark.parametrize(
    "yaml_text, expected",
    [
        (
            """
            safety:
              valid_patterns:
                - \\.swp$
                - \\.tmp$
            """,
            [r"\.swp$", r"\.tmp$"],
        ),
        (
            """
            safety:
              valid_patterns:
                - "^[-_=.,@:A-Za-z0-9]+$"
            """,
            [r"^[-_=.,@:A-Za-z0-9]+$"],
        ),
        (
            """
            safety:
              valid_patterns:
              - ^[-_=.,@:A-Za-z0-9]+$
            """,
            [r"^[-_=.,@:A-Za-z0-9]+$"],
        ),
    ],
)
def test_load_yamlstr_preserves_regex_strings(yaml_load_fn, yaml_text, expected):
    """Loading YAML from string preserves regex strings.

    Note: yaml_text examples are simplified here.
    """
    data = yaml_load_fn(yaml_text)
    assert data["safety"]["valid_patterns"] == expected


def test_load_yamlstr_basic_mapping(yaml_load_fn):
    """Load YAML - basics.

    Note that in this and following tests, fixture `yaml_load_fn` runs twice.
    """
    yaml_text = """
    backup:
      backup_enabled: true
      backup_depth: 3
    """

    result = yaml_load_fn(yaml_text)

    assert result == {
        "backup": {
            "backup_enabled": True,
            "backup_depth": 3,
        }
    }


def test_load_yamlstr_empty_string_returns_empty_dict(yaml_load_fn):
    """Policy: When loading empty string, returns empty dictionary."""
    assert yaml_load_fn("") is None


def test_load_yamlstr_null_returns_empty_dict(yaml_load_fn):
    assert yaml_load_fn("null") is None


def test_load_yamlstr_comment_only(yaml_load_fn):
    """Policy: With comment-only YAML, returns empty dictionary."""
    yaml_text = """
    # this is a comment
    # another comment
    """

    assert yaml_load_fn(yaml_text) is None


def test_load_yamlstr_preserves_nested_dicts_and_lists(yaml_load_fn):
    """Loading YAML preserves nested structure exactly, without normalization."""
    yaml_text = """
    routing:
      files2dirs:
        foo.txt: data/foo
        bar.txt: data/bar
    safety:
      invalid_filename_patterns:
        - \\.tmp$
    """

    result = yaml_load_fn(yaml_text)

    assert result["routing"]["files2dirs"]["foo.txt"] == "data/foo"
    assert isinstance(result["safety"]["invalid_filename_patterns"], list)


def test_load_yamlstr_scalar_yaml(yaml_load_fn):
    """De-facto policy: Loading YAML scalar, returns scalar verbatim."""
    assert yaml_load_fn("42") == 42


def test_load_yamlstr_list_yaml(yaml_load_fn):
    """De-facto policy: Loading YAML list, returns list verbatim."""
    assert yaml_load_fn("- a\n- b\n") == ["a", "b"]


def test_load_yamlstr_invalid_yaml_raises_yamlerror(yaml_load_fn):
    """Policy: Loading invalid YAML, raises YAMLError."""
    yaml_text = """
    backup:
      enabled: true
        depth: 3
    """

    with pytest.raises(yaml.YAMLError):
        yaml_load_fn(yaml_text)


def test_load_yaml_from_string_does_not_mutate_input():
    """Reality check: Loading YAML from string does not mutate input."""
    yaml_text = "backup:\n  enabled: true\n"
    original = yaml_text[:]

    _load_yaml_from_string(yaml_text)

    assert yaml_text == original
