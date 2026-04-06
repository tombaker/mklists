"""Exception classes for types of failure of Mklists semantics."""


class MklistsError(Exception):
    """Base class for all Mklists exceptions."""


class StructureError(MklistsError):
    """Invalid datatree or datadir structure."""


class RuleError(MklistsError):
    """Invalid rule syntax or semantics."""


class FilenameError(RuleError):
    """Invalid filename in rule."""


class DataNotFoundError(MklistsError):
    """Expected data not found."""


class RulesNotFoundError(MklistsError):
    """Expected rules not found."""


class ConfigError(MklistsError):
    """Config file contains unsupported or invalid settings."""


class InitError(MklistsError):
    """Cannot initialize: conflicting files or directories already exist."""


class SafetyError(MklistsError):
    """Data directory fails a safety check."""
