#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import click
import yaml
from ipamcli.libs.phpipam.client import get_token

CONTEXT_SETTINGS = dict(auto_envvar_prefix='IPAMCLI')


class Context(object):

    def log(self, msg, *args):
        """Logs a message to stdout."""
        if args:
            msg %= args
        click.echo(msg)

    def logerr(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if args:
            msg %= args
        click.echo(msg, err=True)


pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                          'commands'))


class ComplexCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
               filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('ipamcli.commands.cmd_' + name,
                             None, None, ['cli'])
        except ImportError:
            return
        return mod.cli


@click.command(cls=ComplexCLI, context_settings=CONTEXT_SETTINGS)
@click.option('-u', '--username',
              default=lambda: os.environ.get('IPAMCLI_USERNAME'),
              help='Username for phpIPAM.')
@click.option('-p', '--password', hide_input=True,
              default=lambda: os.environ.get('IPAMCLI_PASSWORD'),
              help='Password for phpIPAM.')
@click.option('--url',
              default=lambda: os.environ.get('IPAMCLI_URL'),
              help='phpIPAM url.')
@click.option('--vlan-list-path',
              type=click.Path(exists=True),
              default=lambda: os.environ.get('IPAMCLI_VLAN_LIST'),
              help='Path to vlan list configuration file.')
@pass_context
def cli(ctx, username, password, url, vlan_list_path):
    """Console utility for IPAM management with phpIPAM."""
    ctx.username = username
    ctx.password = password
    ctx.url = url
    if(vlan_list_path):
        try:
            with open(vlan_list_path, 'r') as vlan_list:
                ctx.vlan_list = yaml.load(vlan_list, Loader=yaml.FullLoader)
        except Exception:
            ctx.logerr('Oops. VLAN list configuration load exception.')
            sys.exit(1)

    ctx.token = get_token(ctx)
    if ctx.token is None:
        sys.exit(1)
