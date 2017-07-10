# -*- coding: utf-8 -*-
import unittest
from click.testing import CliRunner
from ipamcli.cli import cli


class WithoutCommand(unittest.TestCase):

    def setUp(self):
        with open('tests/files/ip_response.json') as fh:
            self.ip_body = fh.read()

        with open('tests/files/ip_create_response.json') as fh:
            self.ip_create_body = fh.read()

        with open('tests/files/ip_response_multiple.json') as fh:
            self.ip_multiple_body = fh.read()

        with open('tests/files/network_response.json') as fh:
            self.network_body = fh.read()

        self.runner = CliRunner()

    def test_unexist_vlan_list_path(self):
        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan_wrong_path.yml',
             'show'])

        result_require = u'Usage: cli [OPTIONS] COMMAND [ARGS]...\n\nError: Invalid value for "--vlan-list-path": Path "tests/files/vlan_wrong_path.yml" does not exist.\n'
        self.assertEqual(result.output, result_require)
        self.assertEqual(result.exit_code, 2)

    def test_exist_vlan_list_path(self):
        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'show'])

        result_require = u'At least one of the --network / --vlan-id / --vlan-name option must be set.\n'
        self.assertEqual(result.output, result_require)
        self.assertEqual(result.exit_code, 1)


if __name__ == '__main__':
    unittest.main()
