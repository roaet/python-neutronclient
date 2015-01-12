# Copyright 2012 OpenStack Foundation.
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

import logging

from neutronclient.common import exceptions
from neutronclient.neutron import v2_0 as neutronV20


class NeutronClientExtension(neutronV20.NeutronCommand):
    pagination_support = False
    _formatters = {}
    sorting_support = False

    @classmethod
    def get_logger(kls, suffix):
        return logging.getLogger("%s.%s" % (__name__, suffix))


class ClientExtensionList(NeutronClientExtension, neutronV20.ListCommand):
    def get_data(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        neutron_client = self.get_client()
        response = neutron_client.list(self.resource,
                                       self.resource_path,
                                       retrieve_all=True)
        return self.setup_columns(response[self.resource], parsed_args)


class ClientExtensionDelete(NeutronClientExtension, neutronV20.DeleteCommand):
    def run(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _id = parsed_args.id
        neutron_client.delete("%s/%s" % (self.resource_path, _id))
        self.log.debug('Deleted %(resource)s: %(id)s' % {'id': parsed_args.id,
                       'resource': self.resource})


class ClientExtensionCreate(NeutronClientExtension, neutronV20.CreateCommand):
    def get_data(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _extra_values = neutronV20.parse_args_to_dict(self.values_specs)
        neutronV20._merge_args(self, parsed_args, _extra_values,
                               self.values_specs)
        body = self.args2body(parsed_args)
        body[self.resource].update(_extra_values)
        data = neutron_client.post(self.resource_path, body=body)
        self.format_output_data(data)
        info = self.resource in data and data[self.resource] or None
        if info:
            self.log.debug('Created a new %s:' % self.resource)
        else:
            info = {'': ''}
        return zip(*sorted(info.iteritems()))


class ClientExtensionUpdate(NeutronClientExtension, neutronV20.UpdateCommand):
    def run(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _extra_values = neutronV20.parse_args_to_dict(self.values_specs)
        neutronV20._merge_args(self, parsed_args, _extra_values,
                               self.values_specs)
        body = self.args2body(parsed_args)
        if self.resource in body:
            body[self.resource].update(_extra_values)
        else:
            body[self.resource] = _extra_values
        if not body[self.resource]:
            raise exceptions.CommandError(
                "Must specify new values to update %s" % self.resource)
        _id = neutronV20.find_resourceid_by_name_or_id(neutron_client,
                                                       self.resource,
                                                       parsed_args.id)
        neutron_client.put("%s/%s" % (self.resource_path, _id), body)
        self.log.debug(('Updated %(resource)s: %(id)s') %
                       {'id': parsed_args.id, 'resource': self.resource})
        return
