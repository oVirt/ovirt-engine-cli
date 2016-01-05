#
# Copyright (c) 2010 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from ovirtcli.infrastructure.settings import OvirtCliSettings

class Messages():
    class Error():
        OBJECT_IS_IMMUTABLE = '%s "%s" is immutable.'
        NO_SUCH_OPTION = 'option "%s" is not supported, see help for more details.'
        NO_SUCH_OBJECT = '%s %s does not exist.'
        NO_SUCH_ACTION = 'action "%s" does not exist in this context.'
        NO_SUCH_TYPE = 'type "%s" does not exist.'
        NO_SUCH_CONTEXT = 'cannot find any context for type "%s" using given arguments.'
        NO_SUCH_TYPE_OR_ARS_NOT_VALID = 'no such type "%s" or given arguments not valid.'
        NO_IDENTIFIER_OR_NAME = '%s identifier or name required.'
        NO_QUERY_ARGS = '"--query" argument is not available for this type of listing.'
        NO_KWARGS = '"--kwargs" argument is not available for this type of %s.'
        NO_ID = '"--id" argument is not available for this type of %s.'
        NO_NAME = '"--name" argument is not available for this type of show.'
        NO_SPICE_VIEWER_FOUND = 'a SPICE viewer was not found, please install a SPICE viewer (e.g. remote-viewer) first.'
        NO_VNC_VIEWER_FOUND = 'a VNC viewer was not found, please install a VNC viewer (e.g. remote-viewer, or vncviewer) first.'
        NO_SUCH_COMMAND = '%s command was not found, please install it first.'
        NOT_CONNECTED = OvirtCliSettings.PRODUCT.lower() + '-shell is not connected.'
        NO_SUCH_COLLECTION = 'no such collection "%s" or given arguments not valid.'
        NO_CERTIFICATES = 'server CA certificate file must be specified for SSL secured connection.'
        CANNOT_CREATE = 'cannot create "%s" because %s collection is not available or given arguments not valid.'
        CANNOT_CONNECT_TO_VM_DUE_TO_INVALID_STATE = 'cannot connect to vm due to invalid state.'
        CANNOT_START_CONSOLE_CLIENT = '$DISPLAY not set, cannot start a %s client.'
        CANNOT_SET_VM_TICKET = 'could not set a ticket for the vm.'
        CANNOT_CONNECT_TO_BACKEND = 'could NOT reach %s manager\n.'
        CANNOT_CONSTRUCT_COLLECTION_MEMBER_VIEW = 'cannot construct collection/member view, checked variants are:\n%s.\n'
        INVALID_DISPLAY_PROTOCOL = 'display protocol "%s" is not supported.'
        INVALID_COMMAND = 'command "%s" is not valid or not available while not connected.'
        INVALID_ENV_MODE_FOR_CONSOLE = 'not running in a GUI, cannot start a %s viewer.'
        INVALID_OPTION = 'option %s cannot be empty.'
        INVALID_COLLECTION_BASED_OPTION_SYNTAX = 'invalid syntax at "--%s", see help on collection based arguments for more details.'
        INVALID_ARGUMENT_SEGMENT = '"%s" is invalid argument segment.'
        INVALID_OPTION_SEGMENT = '"%s" is invalid segment at option "--%s".'
        INVALID_KWARGS_FORMAT = '"%s" is invalid --kwargs argument, valid format is "x=y;z=q;...".'
        INVALID_KWARGS_CONTENT = '--kwargs constraint cannot be empty.'
        INVALID_ARGUMENT_TYPE = 'value used for the \"%s\" is \"%s\", while %s'
        INVALID_URL_SEGMENT = '"%s" is invalid url format, valid format is http[s]://server:port/path, where path is usually "ovirt-engine/api" or, for older versions of the engine, just "api".'
        MISSING_CONFIGURATION_VARIABLE = 'missing configuration variable: %s.'
        UNSUPPORTED_ATTRIBUTE = 'object construction failure, this could happen if you using unsupported option, please see help for the given command for more details.'
    class Warning():
        CANNOT_FETCH_HOST_CERT_SUBJECT = 'could not fetch host certificate info.'
        CANNOT_FETCH_HOST_CERT_SUBJECT_LEGACY_SDK = 'could not fetch host certificate info cause used backend/sdk does not support it.'
        HOST_IDENTITY_WILL_NOT_BE_VALIDATED = 'host identity will not be validated.'
        ALREADY_CONNECTED = '\nalready connected\n\n'
    class Info():
        POSSIBALE_ARGUMENTS_COMBINATIONS = ',\npossible arguments combinations are %s.'
        POSSIBLE_VM_STATES_FOR_CONSOLE = ',\npossible vm states are %s.'
        ACTION_STATUS = 'action status "%s".'
        STATUS = '\nlast command status: %s'
        PRODUCT_VERSION = "\n%s version: %s.\n"
        NOT_CONNECTED = 'not connected.'
        SUCESS_CONNECT_TO_BACKEND = '\nsuccess: ' + OvirtCliSettings.PRODUCT + ' manager could be reached OK.\n\n'
        SDK_VERSION = 'sdk version    : %s'
        CLI_VERSION = 'cli version    : %s'
        BACKEND_VERSION = 'backend version: %s'
        BACKEND_ENTRY_POINT = 'entry point    : %s'
        PYTHON_VERSION = 'python version : %s'
        PLATFORM = 'platform       : %s'
        ACCEPTED = '\naccepted.\n'
