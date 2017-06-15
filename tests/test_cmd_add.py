# -*- coding: utf-8 -*-
import unittest
import responses
import json
from requests.exceptions import ConnectionError
from click.testing import CliRunner
from ipamcli.cli import cli


class AddCommand(unittest.TestCase):

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

    @responses.activate
    def test_first_empty_vlan_id(self):
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

        responses.add(
            responses.POST,
            'http://noc.rk.local/ip/address/',
            match_querystring=True,
            body=self.ip_create_body, status=201,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add',
             '--first-empty', '--vlan-id', '22',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = u'The entry for ip {}/{} ({}) has been successfully created. The entry ID: {}.\n'.format('10.32.250.2', '24', '255.255.255.0', '880')

        self.assertEqual(json.loads(responses.calls[2].request.body), {"address": "10.32.250.2", "mac": "00:00:00:00:00:02", "fqdn": "fqdn.local", "description": "", "tt": 10})
        self.assertEqual(result.output, result_require)
        self.assertEqual(result.exit_code, 0)

    @responses.activate
    def test_first_empty_vlan_name(self):
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

        responses.add(
            responses.POST,
            'http://noc.rk.local/ip/address/',
            match_querystring=True,
            body=self.ip_create_body, status=201,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add',
             '--first-empty', '--vlan-name', 'smev-vipnet-vlan',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = u'The entry for ip {}/{} ({}) has been successfully created. The entry ID: {}.\n'.format('10.32.250.2', '24', '255.255.255.0', '880')

        self.assertEqual(json.loads(responses.calls[2].request.body), {"address": "10.32.250.2", "mac": "00:00:00:00:00:02", "fqdn": "fqdn.local", "description": "", "tt": 10})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_first_empty_network(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/prefix/?prefix=10.32.250.0/24',
            match_querystring=True,
            body=self.network_body, status=200,
            content_type='application/json')

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?prefix=123',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.POST,
            'http://noc.rk.local/ip/address/',
            match_querystring=True,
            body=self.ip_create_body, status=201,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add',
             '--first-empty', '--network', '10.32.250.0/24',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = u'The entry for ip {}/{} ({}) has been successfully created. The entry ID: {}.\n'.format('10.32.250.2', '24', '255.255.255.0', '880')

        self.assertEqual(json.loads(responses.calls[2].request.body), {"address": "10.32.250.2", "mac": "00:00:00:00:00:02", "fqdn": "fqdn.local", "description": "", "tt": 10})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_last_empty_vlan_id(self):
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

        responses.add(
            responses.POST,
            'http://noc.rk.local/ip/address/',
            match_querystring=True,
            body=self.ip_create_body, status=201,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add',
             '--last-empty', '--vlan-id', '22',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = u'The entry for ip {}/{} ({}) has been successfully created. The entry ID: {}.\n'.format('10.32.250.254', '24', '255.255.255.0', '880')

        self.assertEqual(json.loads(responses.calls[2].request.body), {"address": "10.32.250.254", "mac": "00:00:00:00:00:02", "fqdn": "fqdn.local", "description": "", "tt": 10})
        self.assertEqual(result.output, result_require)
        self.assertEqual(result.exit_code, 0)

    @responses.activate
    def test_last_empty_vlan_name(self):
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

        responses.add(
            responses.POST,
            'http://noc.rk.local/ip/address/',
            match_querystring=True,
            body=self.ip_create_body, status=201,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add',
             '--last-empty', '--vlan-name', 'smev-vipnet-vlan',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = u'The entry for ip {}/{} ({}) has been successfully created. The entry ID: {}.\n'.format('10.32.250.254', '24', '255.255.255.0', '880')

        self.assertEqual(json.loads(responses.calls[2].request.body), {"address": "10.32.250.254", "mac": "00:00:00:00:00:02", "fqdn": "fqdn.local", "description": "", "tt": 10})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_last_empty_network(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/prefix/?prefix=10.32.250.0/24',
            match_querystring=True,
            body=self.network_body, status=200,
            content_type='application/json')

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?prefix=123',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.POST,
            'http://noc.rk.local/ip/address/',
            match_querystring=True,
            body=self.ip_create_body, status=201,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add',
             '--last-empty', '--network', '10.32.250.0/24',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = u'The entry for ip {}/{} ({}) has been successfully created. The entry ID: {}.\n'.format('10.32.250.254', '24', '255.255.255.0', '880')

        self.assertEqual(json.loads(responses.calls[2].request.body), {"address": "10.32.250.254", "mac": "00:00:00:00:00:02", "fqdn": "fqdn.local", "description": "", "tt": 10})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_ip(self):

        responses.add(
            responses.POST,
            'http://noc.rk.local/ip/address/',
            match_querystring=True,
            body=self.ip_create_body, status=201,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add',
             '--ip', '10.32.250.2',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = u'The entry for ip {}/{} ({}) has been successfully created. The entry ID: {}.\n'.format('10.32.250.2', '24', '255.255.255.0', '880')

        self.assertEqual(json.loads(responses.calls[0].request.body), {"address": "10.32.250.2", "mac": "00:00:00:00:00:02", "fqdn": "fqdn.local", "description": "", "tt": 10})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_ip_dublicate(self):

        responses.add(
            responses.POST,
            'http://noc.rk.local/ip/address/',
            match_querystring=True,
            body=self.ip_create_body, status=409,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add',
             '--ip', '10.32.250.2',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = u'The entry for ip {} was not created. Duplicated entry.\n'.format('10.32.250.2')

        self.assertEqual(json.loads(responses.calls[0].request.body), {"address": "10.32.250.2", "mac": "00:00:00:00:00:02", "fqdn": "fqdn.local", "description": "", "tt": 10})
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_first_empty_without_parameters(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add', '--first-empty',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = 'At least one of the --network / --vlan-id / --vlan-name option must be set when use --first-empty option.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_first_empty_with_unexist_vlan_id(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add', '--first-empty', '--vlan-id', 1000,
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = 'No such vlan id in list.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_first_empty_with_unexist_vlan_name(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add', '--first-empty', '--vlan-name', 'test',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = 'No such vlan name in list.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_first_empty_with_invalid_network(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add', '--first-empty', '--network', '999.999.999.999/25',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = 'Network address {} is invalid.\n'.format('999.999.999.999/25')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_with_invalid_ip(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add', '--ip', '999.999.999.999',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = 'IP address {} is invalid.\n'.format('999.999.999.999')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_with_invalid_mac(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add', '--ip', '10.32.250.2',
             '--mac', '999:999:999:999',
             '--task-id', 10])

        result_require = 'MAC address {} is invalid.\n'.format('999:999:999:999')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_without_parameters(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'add', '--task-id', 10])

        result_require = 'At least one of the add option must be set.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_unauthorized(self):

        responses.add(
            responses.POST,
            'http://noc.rk.local/ip/address/',
            match_querystring=True,
            body=self.ip_create_body, status=403,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username1',
             '-p', 'password',
             'add',
             '--ip', '10.32.250.2',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = 'Invalid username or password.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_connection_error(self):

        responses.add(
            responses.POST,
            'http://noc1.rk.local/ip/address/',
            match_querystring=True,
            body=ConnectionError())

        result = self.runner.invoke(
            cli,
            ['-u', 'username1',
             '-p', 'password',
             '--url', 'http://noc1.rk.local',
             'add',
             '--ip', '10.32.250.2',
             '--mac', '00:00:00:00:00:02',
             '--task-id', 10])

        result_require = 'Oops. HTTP API error occured.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)


if __name__ == '__main__':
    unittest.main()
