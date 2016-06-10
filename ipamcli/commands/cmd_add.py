# -*- coding: utf-8 -*-
import click
import netaddr
import requests
import json
import sys
from ipamcli.cli import pass_context
from ipamcli.commands.tools import VLANS, checkMAC, checkIP, get_first_empty


@click.command('add', short_help='add new entry to NOC')
@click.option('--first-empty', is_flag=True, help='search first empty IP address')
@click.option('--network', help='network address for first-empty search')
@click.option('--vlan-id', metavar='<int>', help='vlan id for first-empty search')
@click.option('--vlan-name', help='vlan name for first-empty search')
@click.option('--ip', help='ip address for new entry')
@click.option('--mac', help='mac address for new entry')
@click.option('--fqdn', default='fqdn.local', show_default=True, help='fqdn for new entry')
@click.option('--description', default="", help='description for new entry')
@click.option('--task-id', required=True, help='task id for new entry')
@pass_context
def cli(ctx, first_empty, network, vlan_id, vlan_name, ip, mac, fqdn, description, task_id):
    """Add new entry to NOC."""
    if first_empty:
        if not network and not vlan_id and not vlan_name:
            ctx.logerr('At least one of the --network / --vlan-id / --vlan-name option must be set when use --first-empty option.')
            sys.exit(1)

        if vlan_id:
            if vlan_id not in VLANS:
                ctx.logerr('No such vlan id in list.')
                sys.exit(1)

            else:
                network = VLANS[vlan_id]['prefix']

        elif vlan_name:
            for item in VLANS:
                if VLANS[item]['name'] == vlan_name:
                    network = VLANS[item]['prefix']

            if not network:
                ctx.logerr('No such vlan name in list.')
                sys.exit(1)

        try:
            network = netaddr.IPNetwork(network)

        except netaddr.core.AddrFormatError:
            ctx.logerr('Network address %s is invalid.', network)
            sys.exit(1)

        ip = get_first_empty(ctx, network, verbose=False)

        if not ip:
            ctx.logerr('There is no free IP in network %s.', network)
            sys.exit(1)

    elif ip:
        if not checkIP(ip):
            ctx.logerr('IP address %s is invalid.', ip)
            sys.exit(1)

    else:
        ctx.logerr('At least one of the add option must be set.')
        sys.exit(1)

    if mac:
        if not checkMAC(mac):
            ctx.logerr('MAC address %s is invalid.', mac)
            sys.exit(1)

    payload = {'address': str(ip), 'mac': mac, 'fqdn': fqdn, 'description': description, 'tt': task_id}

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
        sys.exit(1)

    elif r.status_code == 201:
        ctx.log('The entry for ip %s has been successfully created. The entry ID: %s.', ip, r.json()['id'])
