# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = (
    'DanaError',

    'InstallError',
    'FlagValidationError',
    'MissingRequirements',

    'PluginError',
    'ParamProcessingError',
    'ParamValidationError',

    'NetworkError',
    'ScriptRuntimeError',
)


class DanaError(Exception):
    """Default Exception class for packstack installer."""
    def __init__(self, *args, **kwargs):
        super(DanaError, self).__init__(*args)
        self.stdout = kwargs.get('stdout', None)
        self.stderr = kwargs.get('stderr', None)


class PuppetError(Exception):
    """Raised when Puppet will have some problems."""


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


class ParamProcessingError(PluginError):
    pass


class NetworkError(DanaError):
    """Should be used for packstack's network failures."""
    pass



class ExecuteRuntimeError(DanaError):
    """Raised when utils.execute does not end successfully."""


class SequenceError(DanaError):
    """Exception for errors during setup sequence run."""
    pass
