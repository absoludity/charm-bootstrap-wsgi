# Copyright 2013 Canonical Ltd.
#
# Authors:
#  Charm Helpers Developers <juju@lists.ubuntu.com>
"""Charm Helpers ansible - declare the state of your machines.

This helper enables you to declare your machine state, rather than
program it procedurally (and have to test each change to your procedures).
Your install hook can be as simple as:

{{{
import charmhelpers.contrib.ansible

hooks = charmhelpers.contrib.ansible.AnsibleHooks(
    playbook_path="playbook.yaml")

@hooks.hook('install', 'upgrade-charm')
def install():
    charmhelpers.contrib.ansible.install_ansible_support()
}}}

and won't need to change (nor will its tests) when you change the machine
state.

All of your juju config and relation-data are available as template
variables within your playbooks and templates.

An install playbook looks
something like:

{{{
---
- hosts: localhost

  tasks:

    - name: Install dependencies.
      tags:
        - install
        - config-changed
      apt: pkg={{ item }}
      with_items:
        - python-mimeparse
        - python-webob
        - sunburnt

    - name: Setup groups.
        - install
        - config-changed
      group: name={{ item.name }} gid={{ item.gid }}
      with_items:
        - { name: 'deploy_user', gid: 1800 }
        - { name: 'service_user', gid: 1500 }

  ...
}}}


Alternatively, you can apply individual playbooks with:
{{{
charmhelpers.contrib.ansible.apply_playbook('playbooks/install.yaml')
}}}

Read more online about playbooks[1] and standard ansible modules[2].

[1] http://www.ansibleworks.com/docs/playbooks.html
[2] http://www.ansibleworks.com/docs/modules.html
"""
import os
import subprocess
import warnings

import charmhelpers.contrib.templating.contexts
import charmhelpers.core.host
import charmhelpers.core.hookenv
import charmhelpers.fetch


charm_dir = os.environ.get('CHARM_DIR', '')
ansible_hosts_path = '/etc/ansible/hosts'
# Ansible will automatically include any vars in the following
# file in its inventory when run locally.
ansible_vars_path = '/etc/ansible/host_vars/localhost'
available_tags = set([])


def install_ansible_support(from_ppa=True, ppa_location='ppa:rquillo/ansible'):
    """Installs the ansible package.

    By default it is installed from the PPA [1] linked from
    the ansible website [2] or from a ppa specified by a charm config.

    [1] https://launchpad.net/~rquillo/+archive/ansible
    [2] http://www.ansibleworks.com/docs/gettingstarted.html#ubuntu-and-debian

    If from_ppa is empty, you must ensure that the package is available
    from a configured repository.
    """
    if from_ppa:
        charmhelpers.fetch.add_source(ppa_location)
        charmhelpers.fetch.apt_update(fatal=True)
    charmhelpers.fetch.apt_install('ansible')
    with open(ansible_hosts_path, 'w+') as hosts_file:
        hosts_file.write('localhost ansible_connection=local')


def apply_playbook(playbook, tags=None):
    tags = tags or []
    tags = ",".join(tags)
    charmhelpers.contrib.templating.contexts.juju_state_to_yaml(
        ansible_vars_path, namespace_separator='__',
        allow_hyphens_in_keys=False)
    call = [
        'ansible-playbook',
        '-c',
        'local',
        playbook,
    ]
    if tags:
        call.extend(['--tags', '{}'.format(tags)])
    subprocess.check_call(call)


def get_tags_for_playbook(playbook_path):
    """Return all tags within a playbook.

    The charmhelpers lib should not depend on ansible, hence the
    inline imports here.

    Discussion whether --list-tags should be a feature of ansible at
    http://goo.gl/6gXd50
    """
    import ansible.utils
    import ansible.callbacks
    import ansible.playbook
    stats = ansible.callbacks.AggregateStats()
    callbacks = ansible.callbacks.PlaybookRunnerCallbacks(stats)
    runner_callbacks = ansible.callbacks.PlaybookRunnerCallbacks(stats)
    playbook = ansible.playbook.PlayBook(playbook=playbook_path,
                                         callbacks=callbacks,
                                         runner_callbacks=runner_callbacks,
                                         stats=stats)
    myplay = ansible.playbook.Play(playbook, ds=playbook.playbook[0],
                                   basedir=os.path.dirname(playbook_path))

    _, playbook_tags = myplay.compare_tags([])
    playbook_tags.remove('all')
    return playbook_tags


class AnsibleHooks(charmhelpers.core.hookenv.Hooks):
    """Run a playbook with the hook-name as the tag.

    This helper builds on the standard hookenv.Hooks helper,
    but additionally runs the playbook with the hook-name specified
    using --tags (ie. running all the tasks tagged with the hook-name).

    Example:
        hooks = AnsibleHooks(playbook_path='playbooks/my_machine_state.yaml')

        # All the tasks within my_machine_state.yaml tagged with 'install'
        # will be run automatically after do_custom_work()
        @hooks.hook()
        def install():
            do_custom_work()

        # For most of your hooks, you won't need to do anything other
        # than run the tagged tasks for the hook:
        @hooks.hook('config-changed', 'start', 'stop')
        def just_use_playbook():
            pass

        # As a convenience, you can avoid the above noop function by specifying
        # the hooks which are handled by ansible-only and they'll be registered
        # for you:
        # hooks = AnsibleHooks(
        #     'playbooks/my_machine_state.yaml',
        #     default_hooks=['config-changed', 'start', 'stop'])

        if __name__ == "__main__":
            # execute a hook based on the name the program is called by
            hooks.execute(sys.argv)
    """

    def __init__(self, playbook_path, default_hooks=None):
        """Register any hooks handled by ansible.

        default_hooks is now deprecated, as we use ansible to
        determine the supported hooks from the playbook.
        """
        super(AnsibleHooks, self).__init__()

        self.playbook_path = playbook_path

        # The hooks decorator is created at module load time, which on the
        # first run, will be before ansible is itself installed.
        try:
            available_tags.update(get_tags_for_playbook(playbook_path))
        except ImportError:
            available_tags.add('install')

        if default_hooks is not None:
            warnings.warn(
                "The use of default_hooks is deprecated. Ansible is now "
                "used to query your playbook for available tags.",
                DeprecationWarning)
        noop = lambda *args, **kwargs: None
        for hook in available_tags:
            self.register(hook, noop)

    def execute(self, args):
        """Execute the hook followed by the playbook using the hook as tag."""
        super(AnsibleHooks, self).execute(args)
        hook_name = os.path.basename(args[0])

        if hook_name in available_tags:
            charmhelpers.contrib.ansible.apply_playbook(
                self.playbook_path, tags=[hook_name])
