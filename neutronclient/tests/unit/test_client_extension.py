# Copyright 2015 Rackspace Hosting Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import sys

from neutronclient.neutron.v2_0.contrib import fox_sockets
from neutronclient.tests.unit import test_cli20


class CLITestV20ExtensionJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        super(CLITestV20ExtensionJSON, self).setUp(plurals={'tags': 'tag'})

    def test_delete_fox_socket(self):
        """Delete fox socket: myid."""
        resource = 'fox_socket'
        cmd = fox_sockets.FoxInSocketsDelete(test_cli20.MyApp(sys.stdout),
                                             None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)

    def test_update_fox_socket(self):
        """Update fox_socket: myid --name myname."""
        resource = 'fox_socket'
        cmd = fox_sockets.FoxInSocketsUpdate(test_cli20.MyApp(sys.stdout),
                                             None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname'],
                                   {'name': 'myname'})

    def test_create_fox_socket(self):
        """Create fox_socket: myname."""
        resource = 'fox_socket'
        cmd = fox_sockets.FoxInSocketsCreate(test_cli20.MyApp(sys.stdout),
                                             None)
        name = 'myname'
        myid = 'myid'
        args = [name, ]
        position_names = ['name', ]
        position_values = [name, ]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_list_fox_sockets(self):
        """List fox_sockets."""
        resources = 'fox_sockets'
        cmd = fox_sockets.FoxInSocketsList(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_show_fox_socket(self):
        """Show fox_socket: --fields id --fields name myid."""
        resource = 'fox_socket'
        cmd = fox_sockets.FoxInSocketsShow(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'])
