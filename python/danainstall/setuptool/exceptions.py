# -*- coding: utf-8 -*-
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__all__ = (
    'DanaError',
    'InstallError',
    'FlagValidationError',
    'MissingRequirements',
    'PluginError',
    'ParamValidationError',
    'ExecuteRuntimeError',
)


class DanaError(Exception):
    """Default Exception class"""
    def __init__(self, *args, **kwargs):
        super(DanaError, self).__init__(*args)
        self.stdout = kwargs.get('stdout', None)
        self.stderr = kwargs.get('stderr', None)


class MissingRequirements(DanaError):
    """Raised when minimum install requirements are not met."""
    pass


class InstallError(DanaError):
    """Exception for generic errors during setup run."""
    pass


class FlagValidationError(InstallError):
    """Raised when single flag validation fails."""
    pass


class ParamValidationError(InstallError):
    """Raised when parameter value validation fails."""
    pass


class PluginError(DanaError):
    pass


class ExecuteRuntimeError(DanaError):
    """Raised when utils.execute does not end successfully."""
    pass


class LogRuntimeError(DanaError):
    pass



