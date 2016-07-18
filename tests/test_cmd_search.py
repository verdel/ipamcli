# -*- coding: utf-8 -*-
import unittest
import responses
from requests.exceptions import ConnectionError
from click.testing import CliRunner
from ipamcli.cli import cli


class SearchCommand(unittest.TestCase):

    def setUp(self):
        with open('tests/files/ip_response.json') as fh:
            self.ip_body = fh.read()

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

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search',
             '--first-empty', '--vlan-id', '22'])

        result_require = u'First empty IP address in subnet {}:\n{}\n'.format('10.32.250.0/24', '10.32.250.2')

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

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

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search',
             '--first-empty', '--vlan-name', 'smev-vipnet-vlan'])

        result_require = u'First empty IP address in subnet {}:\n{}\n'.format('10.32.250.0/24', '10.32.250.2')

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_first_empty_network(self):

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
             'search',
             '--first-empty', '--network', '10.32.250.0/24'])

        result_require = u'First empty IP address in subnet {}:\n{}\n'.format('10.32.250.0/24', '10.32.250.2')

        self.assertEqual(result.exit_code, 0)
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
            responses.GET,
            'http://noc.rk.local/ip/prefix/?id=123',
            match_querystring=True,
            body=self.network_body, status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search',
             '--ip', '10.32.250.1'])

        result_require = u'ID: {}\nSubnet prefix: {}\nSubnet description: {}\nIP: {}\nMAC: {}\nFQDN: {}\nDescription: {}\nID заявки: {}\n\n'.format(
            879,
            '10.32.250.0/24',
            'Server IP-subnet. IS server',
            '10.32.250.1',
            '00:00:00:00:00:01',
            'fqdn.local',
            '',
            10)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_ip_contains(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?address__contains=10.32.250',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/prefix/?id=123',
            match_querystring=True,
            body=self.network_body, status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search',
             '--ip', '10.32.250',
             '--contains'])

        result_require = u'ID: {}\nSubnet prefix: {}\nSubnet description: {}\nIP: {}\nMAC: {}\nFQDN: {}\nDescription: {}\nID заявки: {}\n\n'.format(
            879,
            '10.32.250.0/24',
            'Server IP-subnet. IS server',
            '10.32.250.1',
            '00:00:00:00:00:01',
            'fqdn.local',
            '',
            10)

        self.assertEqual(result.exit_code, 0)
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
            responses.GET,
            'http://noc.rk.local/ip/prefix/?id=123',
            match_querystring=True,
            body=self.network_body, status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search',
             '--mac', '00:50:56:AE:7F:09'])

        result_require = u'ID: {}\nSubnet prefix: {}\nSubnet description: {}\nIP: {}\nMAC: {}\nFQDN: {}\nDescription: {}\nID заявки: {}\n\n'.format(
            879,
            '10.32.250.0/24',
            'Server IP-subnet. IS server',
            '10.32.250.1',
            '00:00:00:00:00:01',
            'fqdn.local',
            '',
            10)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_task(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?tt=10',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/prefix/?id=123',
            match_querystring=True,
            body=self.network_body, status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search',
             '--task-id', '10'])

        result_require = u'ID: {}\nSubnet prefix: {}\nSubnet description: {}\nIP: {}\nMAC: {}\nFQDN: {}\nDescription: {}\nID заявки: {}\n\n'.format(
            879,
            '10.32.250.0/24',
            'Server IP-subnet. IS server',
            '10.32.250.1',
            '00:00:00:00:00:01',
            'fqdn.local',
            '',
            10)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_ip_empty_result(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?address=10.32.250.1',
            match_querystring=True,
            body="[]", status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search',
             '--ip', '10.32.250.1'])

        result_require = 'There is no record for ip address {}.\n'.format('10.32.250.1')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_mac_empty_result(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?mac=10:10:10:10:10:10',
            match_querystring=True,
            body="[]", status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search',
             '--mac', '10:10:10:10:10:10'])

        result_require = 'There is no record for mac address {}.\n'.format('10:10:10:10:10:10')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_task_empty_result(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?tt=10',
            match_querystring=True,
            body="[]", status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search',
             '--task-id', 10])

        result_require = u'There is no record for ID заявки {}.\n'.format(10)

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_first_empty_without_parameters(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search', '--first-empty'])

        result_require = 'At least one of the --network / --vlan-id / --vlan-name option must be set when use --first-empty option.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_first_empty_with_unexist_vlan_id(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search', '--first-empty', '--vlan-id', 1000])

        result_require = 'No such vlan id in list.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_first_empty_with_unexist_vlan_name(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search', '--first-empty', '--vlan-name', 'test'])

        result_require = 'No such vlan name in list.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_first_empty_with_invalid_network(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search', '--first-empty', '--network', '999.999.999.999/25'])

        result_require = 'Network address {} is invalid.\n'.format('999.999.999.999/25')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_first_empty_with_invalid_ip(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search', '--ip', '999.999.999.999'])

        result_require = 'IP address {} is invalid.\n'.format('999.999.999.999')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_first_empty_with_invalid_mac(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search', '--mac', '999:999:999:999'])

        result_require = 'MAC address {} is invalid.\n'.format('999:999:999:999')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_without_parameters(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'search'])

        result_require = 'At least one of the search option must be set.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_unauthorized(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?tt=10',
            match_querystring=True,
            body="[]", status=403,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username1',
             '-p', 'password',
             'search',
             '--task-id', 10])

        result_require = 'Invalid username or password.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_connection_error(self):

        responses.add(
            responses.GET,
            'http://noc1.rk.local/ip/address/?tt=10',
            match_querystring=True,
            body=ConnectionError())

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             '--url', 'http://noc1.rk.local',
             'search',
             '--task-id', 10])

        result_require = 'Oops. HTTP API error occured.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)


if __name__ == '__main__':
    unittest.main()
