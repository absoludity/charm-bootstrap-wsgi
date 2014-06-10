import unittest

try:
    import mock
except ImportError:
    raise ImportError(
        "Please ensure both python-mock and python-nose are installed.")


from hooks import hooks


class InstallHookTestCase(unittest.TestCase):

    def setUp(self):
        super(InstallHookTestCase, self).setUp()

        patcher = mock.patch('hooks.charmhelpers')
        self.mock_charmhelpers = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_charmhelpers.core.hookenv.config.return_value = {
            'install_deps_from_ppa': False,
        }

        patcher = mock.patch('charmhelpers.contrib.ansible.apply_playbook')
        self.mock_apply_playbook = patcher.start()
        self.addCleanup(patcher.stop)

    def test_install_installs_ansible_support(self):
        hooks.execute(['install'])

        ansible = self.mock_charmhelpers.contrib.ansible
        ansible.install_ansible_support.assert_called_once_with(
            from_ppa=True)

    def test_default_hooks(self):
        """Most of the hooks let ansible do all the work."""
        for hook in ('install', 'upgrade-charm', 'config-changed',
                     'website-relation-changed',
                     'wsgi-file-relation-changed'):
            self.mock_apply_playbook.reset_mock()

            hooks.execute([hook])

            self.assertEqual([
                mock.call('playbook.yml',
                          tags=[hook]),
            ], self.mock_apply_playbook.call_args_list)
