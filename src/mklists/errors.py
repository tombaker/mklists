


class MklistsError(Exception):
    """Base exception for all Mklists errors."""


class StructureError(MklistsError):
    """Raised when repository or datadir structure is invalid."""


class DataNotFoundError(ValueError):
    """Base class for errors with lists of data lines."""


class RulesNotFoundError(ValueError):
    """No rules were found."""


class RuleError(ValueError):
    """Rule does not parse or validate."""


class FilenameError(RuleError):
    """Rule field is not valid as the name of a data file."""


