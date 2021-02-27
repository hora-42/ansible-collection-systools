#!/usr/bin/python

# Copyright: (c) 2021, Holger Ratzel <holger@ratzel.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: authselect

short_description: This module is an interface to authselect

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "0.1.0"

description: This module uses authselect on Fedora and Red Hat systems
  to select the source for authentication information. It does not
  implement all features of authselect yet.

options:
    profile:
        description: This is the profile that should be selected.
        required: true
        type: str
    features:
        description: A list of additional features to use with the
          selected profile.
        required: false
        type: list
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - hora.systools.authselect

author:
    - Holger Ratzel <holger@ratzel.org>
'''

EXAMPLES = r'''
# Simple select a profile
- name: Just select a profile
  hora.authselect:
    profile: sssd

# Select a profile with features
- name: Select profile with features
  hora.authselect:
    profile: sssd
    features:
    - with-sudo
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
profile_requested:
    description: The authentication profile that was requested.
    type: str
    returned: always
    sample: 'sssd'
profile_configured:
    description: The authentication profile that was active after command execution.
    type: str
    returned: always
    sample: 'sssd'
features_requested:
    description: The authentication profile that was requested.
    type: str
    returned: always
    sample: 'sssd'
features_configured:
    description: The authentication profile that was active after command execution.
    type: str
    returned: always
    sample: 'sssd'
    
'''

from ansible.module_utils.basic import AnsibleModule


def get_authselect_state(m):
    import re
    (rc, std_out, std_err) = m.run_command(["/usr/bin/authselect", "current", "--raw"], environ_update=dict(LANG='C'))
    if rc == 2 and std_out == "No existing configuration detected.\n":
        return dict(profile=None,
                    features=None,
                    msg=std_out.rstrip("\n\r"))
    elif rc == 2 and std_err == "":
        pas_out = re.match(r'^(?P<profile>\w+)\W+(?P<features>.*)$', std_out)
        return dict(profile=pas_out.group('profile'),
                    features=re.compile(r'\W+').split(pas_out.group('features')),
                    msg="OK")
    else:
        m.fail_json(rc=rc,
                    stderr=std_err,
                    msg="Failed to execute authselect command with '" + std_err + "'.")


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        profile=dict(type='str', required=True),
        features=dict(type='list', required=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_profile='',
        features=[]
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result['original_profile'] = get_authselect_state(module)
    result['requested_profile'] = module.params['profile']

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
#    if module.params['new']:
#        result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['profile'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
