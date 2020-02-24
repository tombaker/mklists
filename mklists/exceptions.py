"""Exception classes for mklists."""


class MklistsError(SystemExit):
    """Exceptions related to Mklists generally."""


class ConfigError(MklistsError):
    """Exceptions related to configuration."""


class ConfigWarning(Warning):
    """Warning regarding configuration (does not stop execution)."""


class RuleError(MklistsError):
    """Exceptions related to a single rule."""


class RulesError(MklistsError):
    """Exceptions related to sets of rules."""


class DataError(MklistsError):
    """Exceptions related to data (text lists)."""


class BadRegexError(SystemExit):
    """String does not compile as regular expression."""


class BadYamlError(SystemExit):
    """YAML is badly formatted."""


class NotUTF8Error(SystemExit):
    """File is not UTF8-encoded."""


class BadFilenameError(SystemExit):
    """File or directory name uses invalid characters or name patterns."""
