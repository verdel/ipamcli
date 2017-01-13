# -*- coding: utf-8 -*-
import sys
import click
import netaddr
from ipamcli.cli import pass_context
from ipamcli.commands.tools import VLANS, show_network_addresses
from tabulate import tabulate


@click.command('show', short_help='show entry from sub-network in NOC')
@click.option('--network', help='network address')
@click.option('--vlan-id', metavar='<int>', help='vlan id')
@click.option('--vlan-name', help='vlan name')
@click.option('--free-only', is_flag=True, help='show only free IP address from sub-network')
@pass_context
def cli(ctx, network, vlan_id, vlan_name, free_only):
    """Show entry information from NOC."""
    if not network and not vlan_id and not vlan_name:
        ctx.logerr('At least one of the --network / --vlan-id / --vlan-name option must be set.')
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

    resp = show_network_addresses(ctx, network, free_only, verbose=True)

    if resp:
        resp = sorted(resp, key=lambda k: netaddr.IPAddress(k['Address']))
        ctx.log(tabulate(resp, headers="keys", tablefmt='psql'))

    else:
        if vlan_id:
            ctx.log('There is no record for VLAN ID %s.', vlan_id)
            sys.exit(1)

        elif vlan_name:
            ctx.log('There is no record for VLAN Name %s.', vlan_name)
            sys.exit(1)

        elif network:
            ctx.log('There is no record for sub-network %s.', network)
            sys.exit(1)
