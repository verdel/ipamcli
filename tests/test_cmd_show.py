# -*- coding: utf-8 -*-
import unittest
import responses
from requests.exceptions import ConnectionError
from click.testing import CliRunner
from ipamcli.cli import cli


class ShowCommand(unittest.TestCase):

    def setUp(self):
        with open('tests/files/ip_show_response.json') as fh:
            self.ip_body = fh.read()

        with open('tests/files/network_show_response.json') as fh:
            self.network_body = fh.read()

        with open('tests/files/show_console_output_all.txt') as fh:
            self.output_console_all = fh.read()

        with open('tests/files/show_console_output_free_only.txt') as fh:
            self.output_console_free_only = fh.read()

        self.runner = CliRunner()

    @responses.activate
    def test_network_all(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?prefix=123',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/prefix/?prefix=10.32.250.0/24',
            match_querystring=True,
            body=self.network_body, status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'show',
             '--network', '10.32.250.0/24'])

        result_require = self.output_console_all

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_vlan_id_all(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?prefix=123',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/prefix/?prefix=10.32.250.0/24',
            match_querystring=True,
            body=self.network_body, status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'show',
             '--vlan-id', '22'])

        result_require = self.output_console_all

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_vlan_name_all(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?prefix=123',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/prefix/?prefix=10.32.250.0/24',
            match_querystring=True,
            body=self.network_body, status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'show',
             '--vlan-name', 'smev-vipnet-vlan'])

        result_require = self.output_console_all

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_network_free_only(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?prefix=123',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/prefix/?prefix=10.32.250.0/24',
            match_querystring=True,
            body=self.network_body, status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'show',
             '--free-only',
             '--network', '10.32.250.0/24'])

        result_require = self.output_console_free_only

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_vlan_id_free_only(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?prefix=123',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/prefix/?prefix=10.32.250.0/24',
            match_querystring=True,
            body=self.network_body, status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'show',
             '--free-only',
             '--vlan-id', '22'])

        result_require = self.output_console_free_only

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_vlan_name_free_only(self):
        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?prefix=123',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/prefix/?prefix=10.32.250.0/24',
            match_querystring=True,
            body=self.network_body, status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'show',
             '--free-only',
             '--vlan-name', 'smev-vipnet-vlan'])

        result_require = self.output_console_free_only

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    def test_with_unexist_vlan_id(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'show', '--vlan-id', 1000])

        result_require = 'No such vlan id in list.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_with_unexist_vlan_name(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'show', '--vlan-name', 'test'])

        result_require = 'No such vlan name in list.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_with_invalid_network(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'show', '--network', '999.999.999.999/25'])

        result_require = 'Network address {} is invalid.\n'.format('999.999.999.999/25')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_without_parameters(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'show'])

        result_require = 'At least one of the --network / --vlan-id / --vlan-name option must be set.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_unauthorized(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/prefix/?prefix=10.32.250.0/24',
            match_querystring=True,
            body="[]", status=403,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username1',
             '-p', 'password',
             'show',
             '--network', '10.32.250.0/24'])

        result_require = 'Invalid username or password.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_connection_error(self):

        responses.add(
            responses.GET,
            'http://noc1.rk.local/ip/prefix/?prefix=10.32.250.0/24',
            match_querystring=True,
            body=ConnectionError())

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--url', 'http://noc1.rk.local',
             'show',
             '--network', '10.32.250.0/24'])

        result_require = 'Oops. HTTP API error occured.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)


if __name__ == '__main__':
    unittest.main()
