# Copyright 2015 OpenStack Foundation.
# All Rights Reserved.
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

import imp

import mock
import testtools

import neutronclient.shell


class DiscoverTest(testtools.TestCase):

    def create_patch(self, name, func=None):
        patcher = mock.patch(name)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def create_fake_ext(self, name):
        new_ext = imp.new_module(name)
        ext_code = """
from neutronclient.common import extension


class FoxInSocketsList(extension.ClientExtensionList):
    resource = "fox_socket"
    resource_plural = "fox_sockets"
    resource_path = "/%s" % resource_plural
    log = extension.NeutronClientExtension.get_logger('ListFoxSockets')


COMMANDS = {
    "fox-sockets-list": FoxInSocketsList,
}
"""
        exec(ext_code, new_ext.__dict__)
        return new_ext

    def test_discover_via_contrib(self):
        """Discovering extensions without actually deploying fake extensions
        is a little tricky. We will do this by mocking the load with a module
        that is essentially a real extension. We will also ensure that the
        location searched for extensions is sane.
        """
        version = '2.0'
        pkg = 'neutronclient.shell'

        # We make the _discover_extensions do nothing so we can call it
        self.create_patch(pkg + '.NeutronShell._discover_extensions')

        # We make the glob return anything other than __init__ so it runs
        new_glob = self.create_patch('glob.iglob')
        new_glob.return_value = "unimportant_value"

        # We make load_source create a real extension (from eval'ed code)
        new_load_source = self.create_patch('imp.load_source')
        new_load_source.return_value = self.create_fake_ext('fox_in_sockets')

        # Create our shell normally but load contribs manually
        shell = neutronclient.shell.NeutronShell(version)
        shell._load_contrib_extensions(version)

        self.assertEqual(1, new_glob.call_count)
        self.assertIn('v%s/contrib/*.py' % version, new_glob.call_args[0][0])

        # Attempt to find the command we created
        cmd_factory, cmd_name, sub_argv = shell.command_manager.find_command(
            ['fox-sockets-list'])
        self.assertIsNotNone(cmd_factory)
        self.assertEqual(cmd_factory.__module__, 'fox_in_sockets')
        self.assertEqual(cmd_name, 'fox-sockets-list')

    def test_discover_via_externals(self):
        """Discovering extensions without actually deploying fake extensions is
        a little tricky. We will do this by mocking the load with a module that
        is essentially a real extension. We will also ensure that the location
        searched for extensions is sane.
        """
        version = '2.0'
        pkg = 'neutronclient.shell'
        ext_name = 'fox_in_sockets_python_neutronclient_ext'

        # We make the _discover_extensions do nothing so we can call it
        self.create_patch(pkg + '.NeutronShell._discover_extensions')

        # Creates a loader that can be used to load our fake extension
        new_loader = mock.MagicMock()
        new_loader.load_module.return_value = self.create_fake_ext(ext_name)

        # We need to make pkgutil act like we installed an extension
        def return_loader():
            yield (new_loader, ext_name, True)

        new_iter = self.create_patch('pkgutil.iter_modules')
        new_iter.side_effect = return_loader

        # Create our shell normally but load external extensions manually
        shell = neutronclient.shell.NeutronShell(version)
        shell._load_external_extensions()

        self.assertEqual(1, new_iter.call_count)
        self.assertEqual(1, new_loader.load_module.call_count)

        # Attempt to find the command we created
        cmd_factory, cmd_name, sub_argv = shell.command_manager.find_command(
            ['fox-sockets-list'])
        self.assertIsNotNone(cmd_factory)
        self.assertEqual(cmd_factory.__module__, ext_name)
        self.assertEqual(cmd_name, 'fox-sockets-list')
