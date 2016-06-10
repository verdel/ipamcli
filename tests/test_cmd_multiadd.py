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
    def test_add(self):

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
             'multiadd',
             '-c', 'tests/files/test_add.yaml'])

        result_require = u'The entry for ip {} has been successfully created. The entry ID: {}.\nThe entry for ip {} has been successfully created. The entry ID: {}.\n'.format('10.32.250.2', '880', '10.32.250.2', '880')

        self.assertEqual(json.loads(responses.calls[0].request.body), {"address": "10.32.250.2", "mac": "00:00:00:00:00:02", "fqdn": "fqdn.local", "description": "", "tt": 10})
        self.assertEqual(json.loads(responses.calls[1].request.body), {"address": "10.32.250.3", "mac": "00:00:00:00:00:03", "fqdn": "fqdn.local", "description": "", "tt": 10})
        self.assertEqual(result.exit_code, 0)

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
             'multiadd',
             '-c', 'tests/files/test_add.yaml'])

        result_require = u'The entry for ip {} was not created. Duplicated entry.\nThe entry for ip {} was not created. Duplicated entry.\n'.format('10.32.250.2', '10.32.250.3')

        self.assertEqual(json.loads(responses.calls[0].request.body), {"address": "10.32.250.2", "mac": "00:00:00:00:00:02", "fqdn": "fqdn.local", "description": "", "tt": 10})
        self.assertEqual(json.loads(responses.calls[1].request.body), {"address": "10.32.250.3", "mac": "00:00:00:00:00:03", "fqdn": "fqdn.local", "description": "", "tt": 10})
        self.assertEqual(result.output, result_require)

    def test_with_invalid_ip_and_mac(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'multiadd',
             '-c', 'tests/files/test_add_invalid.yaml'])

        result_require = 'IP address {} is invalid.\nMAC address {} is invalid.\n'.format('999.999.999.999', '999:999:999:999')
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
            ['-u', 'username',
             '-p', 'password',
             'multiadd',
             '-c', 'tests/files/test_add.yaml'])

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
            ['-u', 'username',
             '-p', 'password',
             'multiadd',
             '-c', 'tests/files/test_add.yaml'])

        result_require = 'Oops. HTTP API error occured.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

    def test_config_invalid_format(self):

        result = self.runner.invoke(
            cli,
            ['-u', 'username',
             '-p', 'password',
             'multiadd',
             '-c', 'tests/files/test_add_invalid_format.yaml'])

        result_require = 'Error openning file.\n'

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, result_require)

if __name__ == '__main__':
    unittest.main()
