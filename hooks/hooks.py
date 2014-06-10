#!/usr/bin/env python

import sys
import charmhelpers.contrib.ansible

# Create the hooks helper which automatically registers the
# required hooks based on the available tags in your playbook.
# By default, running a hook (such as 'config-changed') will
# result in running all tasks tagged with that hook name.
hooks = charmhelpers.contrib.ansible.AnsibleHooks(
    playbook_path='playbook.yml')


@hooks.hook('install', 'upgrade-charm')
def install():
    """Install ansible.

    The hook() helper decorating this install function ensures that after this
    function finishes, any tasks in the playbook tagged with install are
    executed.
    """
    charmhelpers.contrib.ansible.install_ansible_support(from_ppa=True)


if __name__ == "__main__":
        hooks.execute(sys.argv)
