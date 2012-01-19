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


from ovirtcli.field import *

_mapping_data = {}

#FIXME

_mapping_data = {
    params.BaseResource: [
        StringField('id', 'A unique ID for this object', 'S'),
        StringField('name', 'A unique name for this object', 'SL'),
        StringField('description', 'A textual description', 'S'),
    ],
    params.DataCenter: [
        StringField('id', 'A unique ID for this datacenter', 'S'),
        StringField('name', 'The name of this datacenter', 'SLUC'),
        StringField('description', 'A description for this datacenter', 'SUC'),
        StringField('status', 'The status of this datacenter', 'SL',
                    attribute='status.state'),
        StringField('storage_type', 'The type of storage for this datacenter', 'SLC'),
        VersionField('version', 'The current compatibility version', 'SLC'),
        VersionListField('supported_versions', 'Available compatiblity version', 'S')
    ],
    params.NIC: [
        StringField('id', 'A unique ID for this NIC', 'S'),
        StringField('name', 'The name of this NIC', 'SLUC'),
        StringField('description', 'A description for this NIC', 'SUC'),
        ReferenceField('network', 'A network for this NIC', 'CUS'),
#        StringField('status', 'The status of this NIC', 'SL',
#                    attribute='status.state'),
        StringField('interface', 'The interface of this NIC', 'SLC'),
    ],
    params.VM: [
        StringField('id', 'The unique ID for this VM', 'S'),
        StringField('name', 'A unique name for this VM', 'CULS'),
        StringField('description', 'A textual description', 'CUS'),
        StringField('status', 'The VM status', 'LS',
                    attribute='status.state'),
        IntegerField('memory', 'Memory size in MiB', 'CUS', scale=1024 ** 2),
        StringField('os', 'The operating system', 'CUS', attribute='os.type'),
        BooleanField('ha', 'Restart this VM in case it fails', 'CUS',
                     attribute='highly_available'),
        StringField('display', 'The display type', 'CUS',
                  attribute='display.type'),
        IntegerField('monitors', 'The number of monitors', 'CUS',
                     attribute='display.monitors', min=1, max=4),
        BooleanField('stateless', 'Do not save state', 'CUS'),
        ReferenceField('template', 'The template this VM is based on', 'CS'),
        ReferenceField('cluster', 'The cluster this VM resides in', 'CUS')
    ],
    params.Action:  [
        StringField('status', 'The action status', 'S',
                    attribute='status.state'),
        BooleanField('pause', 'Start the VM in paused mode', 'C',
                     scope='VM:start'),
        ReferenceField('host', 'Start the VM on this host', 'C',
                       scope='VM:start', attribute='vm.host'),
        BooleanField('stateless', 'Start the VM in stateless mode', 'C',
                     scope='VM:start', attribute='vm.stateless'),
        StringField('display', 'Display protocol', 'C',
                     scope='VM:start', attribute='vm.display.type'),
        StringField('ticket', 'The ticket value', 'S',
                     scope='VM:ticket', attribute='ticket.value_'),
        IntegerField('expiry', 'The ticket expiration time', 'SC',
                     scope='VM:ticket', attribute='ticket.expiry')
    ],
    params.Disk: [
        StringField('name', 'The name of the disk', 'LS'),
        StringField('interface', 'The disk interface ("IDE" or "VIRTIO")', 'CLSU'),
        IntegerField('size', 'The disk size in MiB', 'CLSU', scale=1024 ** 2),
        StringField('format', 'The disk format ("COW" or "RAW")', 'CLSU'),
        StringField('status', 'The disk status', 'LS',
                    attribute='status.state'),
        StringField('type', 'The disk type', 'CSU'),
        BooleanField('sparse', 'This is a sparse disk', 'CSU'),
        BooleanField('bootable', 'This is a bootable disk', 'CSU'),
        BooleanField('wipe', 'This is a bootable disk', 'CSU',
                     attribute='wipe_after_delete'),
        BooleanField('errors', 'Propagate errors', 'CS',
                     attribute='propagate_errors'),
        ReferenceListField('storagedomain', 'The storage domain for this disk',
                       'CS', attribute='storage_domains.storage_domain')
    ],
    params.Statistic: [
        StringField('id', 'A unique ID for this statistic', 'S'),
        StringField('name', 'The statistic name', 'SL'),
        StringField('description', 'A description for this statistic', 'S'),
        StringField('type', 'The statistic type', 'SL'),
        StatisticValueField('value', 'The current value', 'SL',
                            attribute='values'),
        StringField('unit', 'The unit for this statistic', 'SL')
    ],
    params.File: [
        StringField('name', 'The file name', 'SL')
    ],
    params.Host: [
        StringField('id', 'A unique ID for this host', 'S'),
        StringField('name', 'The name of this host', 'SLUC'),
        StringField('description', 'A description for this host', 'SUC'),
        StringField('status', 'The status of this host', 'SL',
                    attribute='status.state'),
        StringField('address', 'The address of this host', 'SUC'),
        StringField('root_password', 'The root password of this host', 'C')
    ],
    params.Cluster: [
        StringField('id', 'A unique ID for this cluster', 'S'),
        StringField('name', 'The name of this cluster', 'SLUC'),
        StringField('description', 'A description for this cluster', 'SUC'),
        ReferenceField('datacenter', 'The dataCenter of this cluster', 'CS', attribute='data_center'),
        StringField('cpu', 'The supported CPUs for this cluster', 'CS', attribute='cpu.id')
    ]
}

def get_fields(typ, flags, scope=None):
    """Return the list of fields for a type/action."""
    if typ not in _mapping_data:
        return _mapping_data[params.BaseResource]
        return None
    fields = _mapping_data[typ]
    for flag in flags:
        fields = filter(lambda f: flag in f.flags, fields)
    fields = filter(lambda f: f.scope in (None, scope) , fields)
    return fields
