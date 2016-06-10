# -*- coding: utf-8 -*-
import unittest
import responses
import json
from requests.exceptions import ConnectionError
from click.testing import CliRunner
from ipamcli.cli import cli


class EditCommand(unittest.TestCase):

    def setUp(self):
        with open('tests/files/ip_response.json') as fh:
            self.ip_body = fh.read()

        with open('tests/files/ip_response_multiple.json') as fh:
            self.ip_multiple_body = fh.read()

        with open('tests/files/network_response.json') as fh:
            self.network_body = fh.read()

        self.runner = CliRunner()

    def test_without_parameters(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'edit'])

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
             'edit',
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
             'edit',
             '--task-id', 10])

        result_require = 'Oops. HTTP API error occured.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_invalid_ip(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'edit', '--ip', '999.999.999.999'])

        result_require = 'IP address {} is invalid.\n'.format('999.999.999.999')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_invalid_mac(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'edit', '--mac', '999:999:999:999'])

        result_require = 'MAC address {} is invalid.\n'.format('999:999:999:999')

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_empty_result(self):

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
             'edit',
             '--ip', '10.32.250.2',
             '--new-ip', '10.32.250.3'])

        result_require = 'There is no record. For edit operation must be specified at least one entry.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_multiple_result(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?mac=00:00:00:00:00:01',
            match_querystring=True,
            body=self.ip_multiple_body, status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'edit',
             '--mac', '00:00:00:00:00:01',
             '--new-ip', '10.32.250.3'])

        result_require = 'There is multiple entries. For edit operation must be specified only one entry.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    @responses.activate
    def test_edit_by_ip(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?address=10.32.250.1',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.PUT,
            'http://noc.rk.local/ip/address/879/',
            match_querystring=True,
            body="", status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'edit',
             '--ip', '10.32.250.1',
             '--new-ip', '10.32.250.2',
             '--new-mac', '00:00:00:00:00:02',
             '--new-fqdn', 'test.local',
             '--new-description', 'test',
             '--new-task-id', 20])

        result_require = 'The entry has been successfully updated.\n'

        self.assertEqual(json.loads(responses.calls[1].request.body), {"address": "10.32.250.2", "mac": "00:00:00:00:00:02", "fqdn": "test.local", "description": "test", "tt": 20})
        self.assertEqual(result.output, result_require)
        self.assertEqual(result.exit_code, 0)

    @responses.activate
    def test_edit_by_mac(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?mac=00:00:00:00:00:01',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.PUT,
            'http://noc.rk.local/ip/address/879/',
            match_querystring=True,
            body="", status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'edit',
             '--mac', '00:00:00:00:00:01',
             '--new-ip', '10.32.250.2',
             '--new-mac', '00:00:00:00:00:02',
             '--new-fqdn', 'test.local',
             '--new-description', 'test',
             '--new-task-id', 20])

        result_require = 'The entry has been successfully updated.\n'

        self.assertEqual(json.loads(responses.calls[1].request.body), {"address": "10.32.250.2", "mac": "00:00:00:00:00:02", "fqdn": "test.local", "description": "test", "tt": 20})
        self.assertEqual(result.output, result_require)
        self.assertEqual(result.exit_code, 0)

    @responses.activate
    def test_edit_by_task_id(self):

        responses.add(
            responses.GET,
            'http://noc.rk.local/ip/address/?tt=10',
            match_querystring=True,
            body=self.ip_body, status=200,
            content_type='application/json')

        responses.add(
            responses.PUT,
            'http://noc.rk.local/ip/address/879/',
            match_querystring=True,
            body="", status=200,
            content_type='application/json')

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'edit',
             '--task-id', 10,
             '--new-ip', '10.32.250.2',
             '--new-mac', '00:00:00:00:00:02',
             '--new-fqdn', 'test.local',
             '--new-description', 'test',
             '--new-task-id', 20])

        result_require = 'The entry has been successfully updated.\n'

        self.assertEqual(json.loads(responses.calls[1].request.body), {"address": "10.32.250.2", "mac": "00:00:00:00:00:02", "fqdn": "test.local", "description": "test", "tt": 20})
        self.assertEqual(result.output, result_require)
        self.assertEqual(result.exit_code, 0)

if __name__ == '__main__':
    unittest.main()
