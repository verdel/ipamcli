#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import click

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
@click.option('-u', '--username', required=True,
              default=lambda: os.environ.get('IPAMCLI_USERNAME'),
              help='Username for NOC.')
@click.option('-p', '--password', prompt=True, hide_input=True, required=True,
              default=lambda: os.environ.get('IPAMCLI_PASSWORD'),
              help='Password for NOC.')
@click.option('--url', default='http://noc.rk.local',
              show_default=True, help='NOC url.')
@pass_context
def cli(ctx, username, password, url):
    """Console utility for IPAM management with NOC."""
    ctx.username = username
    ctx.password = password
    ctx.url = url
