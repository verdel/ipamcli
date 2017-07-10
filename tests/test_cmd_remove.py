# -*- coding: utf-8 -*-
import unittest
import responses
from requests.exceptions import ConnectionError
from click.testing import CliRunner
from ipamcli.cli import cli


class RemoveCommand(unittest.TestCase):

    def setUp(self):
        with open('tests/files/ip_response.json') as fh:
            self.ip_body = fh.read()

        with open('tests/files/ip_response_multiple.json') as fh:
            self.ip_multiple_body = fh.read()

        with open('tests/files/network_response.json') as fh:
            self.network_body = fh.read()

        self.runner = CliRunner()

    @responses.activate
    def test_id(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?id=879',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.DELETE,
            'http://noc.rk.local/ip/address/879',
            match_querystring=True,
            body="[]", status=204,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'remove',
             '--id', '879'])

        result_require = 'The entry has been successfully removed.\n'

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_with_unexist_id(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?id=878',
            match_querystring=True,
            body="[]", status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'remove',
             '--id', '878'])

        result_require = 'There is no entry for id {}.\n'.format(878)

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_ip(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?address=10.32.250.1',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.DELETE,
            'http://noc.rk.local/ip/address/879',
            match_querystring=True,
            body="", status=204,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'remove',
             '--ip', '10.32.250.1'])

        result_require = 'The entry has been successfully removed.\n'

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_with_unexist_ip(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?address=10.32.250.2',
            match_querystring=True,
            body="[]", status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'remove',
             '--ip', '10.32.250.2'])

        result_require = 'There is no entry for ip {}.\n'.format('10.32.250.2')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_mac(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?mac=00:50:56:AE:7F:09',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.DELETE,
            'http://noc.rk.local/ip/address/879',
            match_querystring=True,
            body="", status=204,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'remove',
             '--mac', '00:50:56:AE:7F:09'])

        result_require = 'The entry has been successfully removed.\n'

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_with_mac_multiple_entries(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?mac=00:50:56:AE:7F:09',
            match_querystring=True,
            body=self.ip_multiple_body, status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'remove',
             '--mac', '00:50:56:AE:7F:09'])

        result_require = 'There is multiple entry for MAC {}. For a remove operation must be specified only one entry.\n'.format('00:50:56:AE:7F:09')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_with_unexist_mac(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?mac=00:50:56:AE:7F:01',
            match_querystring=True,
            body="[]", status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'remove',
             '--mac', '00:50:56:AE:7F:01'])

        result_require = 'There is no entry for mac {}.\n'.format('00:50:56:AE:7F:01')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_connection_error(self):

        responses.add(
            responses.GET,
            'http://noc1.rk.local/ip/address/?address=10.32.250.1',
            match_querystring=True,
            body=ConnectionError())

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             '--url', 'http://noc1.rk.local',
             'remove',
             '--ip', '10.32.250.1'])

        result_require = 'Oops. HTTP API error occured.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_without_parameters(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'remove'])

        result_require = 'At least one of the remove option must be set.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_unauthorized(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?address=10.32.250.1',
            match_querystring=True,
            body="[]", status=403,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username1',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'remove',
             '--ip', '10.32.250.1'])

        result_require = 'Invalid username or password.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_error(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?address=10.32.250.1',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.DELETE,
            'http://noc.rk.local/ip/address/879',
            match_querystring=True,
            body="[]", status=500,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'remove',
             '--ip', '10.32.250.1'])

        result_require = 'Error deleting entry.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_with_invalid_ip(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'remove', '--ip', '999.999.999.999'])

        result_require = 'IP address {} is invalid.\n'.format('999.999.999.999')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_first_empty_with_invalid_mac(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--vlan-list-path', 'tests/files/vlan.yml',
             'remove', '--mac', '999:999:999:999'])

        result_require = 'MAC address {} is invalid.\n'.format('999:999:999:999')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)


if __name__ == '__main__':
    unittest.main()
