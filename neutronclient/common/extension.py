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

import glob
import imp
import os
import pkgutil

import pkg_resources

from neutronclient.neutron import v2_0 as neutronV20


def _discover_via_contrib_path(version):
    module_path = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    version_str = "v%s" % version.replace('.', '_')
    ext_path = os.path.join(module_path, 'neutron', version_str, "contrib")
    ext_glob = os.path.join(ext_path, "*.py")
    for ext_path in glob.iglob(ext_glob):
        name = os.path.basename(ext_path)[:-3]
        if name.startswith('_'):
            continue

        module = imp.load_source(name, ext_path)
        yield name, module


def _discover_via_python_path():
    for (module_loader, name, _ispkg) in pkgutil.iter_modules():
        if name.endswith('_python_neutronclient_ext'):
            if not hasattr(module_loader, 'load_module'):
                # Python 2.6 compat: actually get an ImpImporter obj
                module_loader = module_loader.find_module(name)

            module = module_loader.load_module(name)
            yield name, module


def _discover_via_entry_points():
    for ep in pkg_resources.iter_entry_points('neutronclient.extension'):
        name = ep.name
        module = ep.load()

        yield name, module


class NeutronClientExtension(neutronV20.NeutronCommand):
    pagination_support = False
    _formatters = {}
    sorting_support = False


class ClientExtensionShow(NeutronClientExtension, neutronV20.ShowCommand):
    def get_data(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        return super(ClientExtensionShow, self).get_data(parsed_args)


class ClientExtensionList(NeutronClientExtension, neutronV20.ListCommand):
    def get_data(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        return super(ClientExtensionList, self).get_data(parsed_args)


class ClientExtensionDelete(NeutronClientExtension, neutronV20.DeleteCommand):
    def run(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        return super(ClientExtensionDelete, self).run(parsed_args)


class ClientExtensionCreate(NeutronClientExtension, neutronV20.CreateCommand):
    def get_data(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        return super(ClientExtensionCreate, self).get_data(parsed_args)


class ClientExtensionUpdate(NeutronClientExtension, neutronV20.UpdateCommand):
    def run(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        return super(ClientExtensionUpdate, self).run(parsed_args)
