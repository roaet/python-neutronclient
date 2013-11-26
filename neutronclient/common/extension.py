import logging

from neutronclient.common import exceptions
from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.openstack.common.gettextutils import _


class NeutronExtension(neutronV20.NeutronCommand):
    pagination_support = False
    _formatters = {}
    sorting_support = False

    @classmethod
    def get_logger(kls, suffix):
        return logging.getLogger("%s.%s" % (__name__, suffix))


class ExtensionList(NeutronExtension, neutronV20.ListCommand):
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


class ExtensionDelete(NeutronExtension, neutronV20.DeleteCommand):
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
        print >>self.app.stdout, (_('Deleted %(resource)s: %(id)s')
                                  % {'id': parsed_args.id,
                                     'resource': self.resource})


class ExtensionCreate(NeutronExtension, neutronV20.CreateCommand):
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
            print >>self.app.stdout, _('Created a new %s:') % self.resource
        else:
            info = {'': ''}
        return zip(*sorted(info.iteritems()))


class ExtensionUpdate(neutronV20.UpdateCommand):
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
        print >>self.app.stdout, (
            _('Updated %(resource)s: %(id)s') %
            {'id': parsed_args.id, 'resource': self.resource})
        return
