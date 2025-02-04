# Copyright 2021 Canonical
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tools for directly augmenting deployed machine operating system."""

import zaza.model
import zaza.utilities.juju


def install_modules_extra(unit_name, model_name=None):
    """Install the linux-modules-extra package for current kernel version.

    :param unit_name: Name of unit to operate on
    :type unit_name: str
    :param model_name: Name of model to query
    :type model_name: Optional[str]
    :raises: zaza.model.CommandRunFailed
    """
    cmd = 'apt -y install linux-modules-extra-$(uname -r)'
    zaza.utilities.juju.remote_run(unit_name, cmd, model_name=model_name)


def load_kernel_module(unit_name, module_name, module_arguments=None,
                       model_name=None):
    """Load kernel module on unit.

    :param unit_name: Name of unit to operate on
    :type unit_name: str
    :param module_name: Name of kernel module to load
    :type module_name: str
    :param module_arguments: Extra arguments to pass to module on load
    :type module_arguments: Optional[str]
    :param model_name: Name of model to query
    :type model_name: Optional[str]
    :returns: The function is called for its side effects and does not return.
    :raises: zaza.model.CommandRunFailed
    """
    cmd = 'modprobe {} {}'.format(module_name, module_arguments or '')
    zaza.utilities.juju.remote_run(unit_name, cmd, model_name=model_name)


def is_container(unit_name, model_name=None):
    """Check whether the machine the unit is running on is a container.

    :param unit_name: Name of unit to operate on
    :type unit_name: str
    :param model_name: Name of model to query
    :type model_name: Optional[str]
    """
    cmd = 'systemd-detect-virt --container'
    try:
        zaza.utilities.juju.remote_run(unit_name, cmd, model_name=model_name)
        return True
    except zaza.model.CommandRunFailed:
        return False


def add_netdevsim(unit_name, device_id, port_count, model_name=None):
    """Add netdevsim device.

    Ensure the linux-modules-extra package is installed, load the `netdevsim`
    kernel module and add a netdevsim device. This function is idempotent.

    :param unit_name: Name of unit to operate on
    :type unit_name: str
    :param device_id: Device ID to use
    :type device_id: int
    :param port_count: Number of ports per device
    :type port_count: int
    :returns: List of device names
    :rtype: List[str]
    """
    install_modules_extra(unit_name, model_name=model_name)
    load_kernel_module(unit_name, 'netdevsim', model_name=model_name)
    cmd = ('test -d /sys/devices/netdevsim{device_id} || '
           'echo "{device_id} {port_count}" > /sys/bus/netdevsim/new_device'
           .format(device_id=str(device_id), port_count=str(port_count)))
    zaza.utilities.juju.remote_run(unit_name, cmd, model_name=model_name)
    return [
        'eni{}np{}'.format(device_id, port)
        for port in range(1, port_count + 1)
    ]
