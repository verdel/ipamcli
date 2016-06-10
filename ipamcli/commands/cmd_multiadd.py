# -*- coding: utf-8 -*-
import sys
import click
import requests
import json
import yaml
from ipamcli.cli import pass_context
from ipamcli.commands.tools import checkMAC, checkIP


def add_entry(ctx, ip, **kwargs):
    if not checkIP(ip):
            ctx.logerr('IP address %s is invalid.', ip)
            return

    if 'fqdn' not in kwargs:
        kwargs['fqdn'] = 'fqdn.local'

    if 'description' not in kwargs:
        kwargs['description'] = ''

    if 'task_id' not in kwargs:
        ctx.logerr('Task_id must be specify for IP address %s.', ip)
        return

    if 'mac' in kwargs:
        if not checkMAC(kwargs['mac']):
            ctx.logerr('MAC address %s is invalid.', kwargs['mac'])
            return
    else:
        kwargs['mac'] = None

    payload = {'address': str(ip), 'mac': kwargs['mac'], 'fqdn': kwargs['fqdn'], 'description': kwargs['description'], 'tt': kwargs['task_id']}

    try:
        r = requests.post('{}/ip/address/'.format(ctx.url),
                          auth=(ctx.username, ctx.password),
                          data=json.dumps(payload))
    except:
        ctx.logerr('Oops. HTTP API error occured.')
        sys.exit(1)

    if r.status_code == 403:
        ctx.logerr('Invalid username or password.')
        sys.exit(1)

    elif r.status_code == 409:
        ctx.logerr('The entry for ip %s was not created. Duplicated entry.', ip)

    elif r.status_code == 201:
        ctx.log('The entry for ip %s has been successfully created. The entry ID: %s.', ip, r.json()['id'])


@click.command('multiadd', short_help='add new entry from file to NOC')
@click.option('-c', '--config',
              type=click.Path(exists=True),
              help='path to file with new entry or entries information')
@pass_context
def cli(ctx, config):
    """Add multiple entry from file to NOC.

       \b
       Config file type must be yaml.
       Example file format:
       \b
       ---
       - ip: 10.10.10.1
         mac: 00:00:00:00:00:01
         fqdn: test01.local
         description: test1
         task_id: 1
       \b
       - ip: 10.10.10.2
         mac: 00:00:00:00:00:02
         fqdn: test02.local
         description: test2
         task_id: 2

       Options ip and task_id is required. Mac, fqdn, description are optional.
    """
    try:
        config = yaml.load(file(config, 'r'))

    except:
        ctx.logerr('Error openning file.')
        sys.exit(1)

    for item in config:
        if item['ip']:
            ip = item['ip']
            item.pop('ip')
            add_entry(ctx, ip, **item)
