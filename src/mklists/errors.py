"""Exception classes for types of failure of Mklists semantics."""


class MklistsError(Exception):
    """Base class for all Mklists exceptions."""


class StructureError(MklistsError):
    """Invalid repository or datadir structure."""


class RuleError(ValueError):
    """Invalid rule syntax or semantics."""


class FilenameError(RuleError):
    """Invalid filename in rule."""


class DataNotFoundError(MklistsError):
    """Expected data not found."""


class RulesNotFoundError(MklistsError):
    """Expected rules not found."""
