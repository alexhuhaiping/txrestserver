# Copyright 2020, Boling Consulting Solutions
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from twisted.web.resource import NoResource, IResource
from twisted.cred.portal import IRealm
from zope.interface import implementer

from txrestserver.txrestapi.json_resource import JsonAPIResource                # pylint: disable=import-error
from txrestserver.txrestapi.methods import GET  # , POST, PUT, DELETE, ALL      # pylint: disable=import-error

VERSION_PATH = b'^/version'
MY_VERSION = '0.1.0'

EXAMPLE_LIST_PATH = b'^/examples'

EXAMPLE_BASE_PATH = b'^/example'
EXAMPLE_PATH = EXAMPLE_BASE_PATH + b'/(?P<key>[^/]*)/'

EXAMPLE_ENTRIES = {
    'abc': {
        'entry_1': 123,
        'entry_2': 'This is a test',
    },
    'xyz': {
        'entry_1': 456,
        'entry_2': 'Another test',
        'entry_3': [1, 2, 3, 4, 5, 6],
    },
}


class RestAPI(JsonAPIResource):
    """ Base resources that allow access without any credentials """
    @staticmethod
    @GET(VERSION_PATH)
    def _on_get_version(_request):
        return MY_VERSION

    @staticmethod
    @GET(EXAMPLE_LIST_PATH)
    def _on_get_example_list(_request):
        return list(EXAMPLE_ENTRIES.keys())

    @staticmethod
    @GET(EXAMPLE_PATH + b'?')
    def _on_get_example_info(_request, key):
        value = EXAMPLE_ENTRIES.get(key)
        if value is None:
            return NoResource("Example with key '{}' not found".format(key))

        return value


@implementer(IRealm)
class RestApiRealm:
    """
    A realm which gives out L{GuardedResource} instances for authenticated users.
    """
    @staticmethod
    def requestAvatar(_avatarId, _mind, *interfaces):      # pylint: disable=invalid-name
        """
        Return avatar which provides one of the given interfaces.

        @param _avatarId: a string that identifies an avatar, as returned by
            L{ICredentialsChecker.requestAvatarId<twisted.cred.checkers.ICredentialsChecker.requestAvatarId>}
            (via a Deferred).  Alternatively, it may be
            C{twisted.cred.checkers.ANONYMOUS}.
        @param _mind: usually None.  See the description of mind in
            L{Portal.login}.
        @param interfaces: the interface(s) the returned avatar should
            implement, e.g.  C{IMailAccount}.  See the description of
            L{Portal.login}.

        @returns: a deferred which will fire a tuple of (interface,
            avatarAspect, logout), or the tuple itself.  The interface will be
            one of the interfaces passed in the 'interfaces' argument.  The
            'avatarAspect' will implement that interface.  The 'logout' object
            is a callable which will detach the mind from the avatar.
        """
        if IResource in interfaces:
            return IResource, RestAPI(), lambda: None

        raise KeyError("None of the requested interfaces are supported")
