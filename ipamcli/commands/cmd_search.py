# -*- coding: utf-8 -*-
import sys
import click
import netaddr
from ipamcli.cli import pass_context
import ipamcli.libs.phpipam.client as phpipam


@click.command('search', short_help='search entry in phpIPAM')
@click.option('--ip', help='ip address of entry to search')
@click.option('--hostname', help='hostname of entry to search')
@click.option('--first-empty', is_flag=True, help='search first empty IP address')
@click.option('--last-empty', is_flag=True, help='search last empty IP address')
@click.option('--network', help='network address for first-empty search')
@click.option('--vlan-id', metavar='<int>', help='vlan id for first-empty search')
@click.option('--vlan-name', help='vlan name for first-empty search')
@pass_context
def cli(ctx, ip, hostname, first_empty, last_empty, network, vlan_id, vlan_name):
    """Search entry information in phpIPAM."""
    if first_empty or last_empty:
        if not network and not vlan_id and not vlan_name:
            ctx.logerr('At least one of the --network / --vlan-id / --vlan-name option must be set when use --first-empty option.')
            sys.exit(1)

        if vlan_id:
            if vlan_id not in ctx.vlan_list:
                ctx.logerr('No such vlan id in list.')
                sys.exit(1)

            else:
                network = ctx.vlan_list[vlan_id]['prefix']

        elif vlan_name:
            for item in ctx.vlan_list:
                if ctx.vlan_list[item]['name'] == vlan_name:
                    network = ctx.vlan_list[item]['prefix']

            if not network:
                ctx.logerr('No such vlan name in list.')
                sys.exit(1)

        try:
            network = netaddr.IPNetwork(network)

        except netaddr.core.AddrFormatError:
            ctx.logerr('Network address %s is invalid.', network)
            sys.exit(1)

        if first_empty:
            ip = phpipam.get_first_empty(ctx, network)
        elif last_empty:
            ip = phpipam.get_last_empty(ctx, network)

        if ip is None:
            sys.exit(1)
        else:
            ctx.log('Empty IP address in subnet %s(%s):\n%s',
                    str(network), phpipam.get_network_mask_by_subnet(str(network)), ip)

    else:
        if ip:
            if not phpipam.checkIP(ip):
                ctx.logerr('IP address %s is invalid.', ip)
                sys.exit(1)

            try:
                resp = phpipam.search_by_ip(ctx, ip)
            except Exception:
                ctx.logerr('Oops. HTTP API error occured.')
                sys.exit(1)

        elif hostname:
            try:
                resp = phpipam.search_by_hostname(ctx, hostname)
            except Exception:
                ctx.logerr('Oops. HTTP API error occured.')
                sys.exit(1)

        else:
            ctx.logerr('At least one of the search option must be set.')
            sys.exit(1)

        if resp:
            resp = sorted(resp, key=lambda k: netaddr.IPAddress(k['ip']))
            for item in resp:
                subnet = phpipam.get_subnet_by_id(ctx, item['subnetId'])
                ctx.log(u'ID: %s\nSubnet prefix: %s\nSubnet netmask: %s\nSubnet description: %s\nIP: %s\nMAC: %s\nFQDN: %s\nDescription: %s\n',
                        item['id'],
                        '{}/{}'.format(subnet['subnet'], subnet['mask']),
                        phpipam.get_network_mask_by_subnet('{}/{}'.format(subnet['subnet'], subnet['mask'])),
                        subnet['description'],
                        item['ip'],
                        item['mac'],
                        item['hostname'],
                        item['description'])

        else:
            if ip:
                ctx.log('There is no record for ip address %s.', ip)
                sys.exit(1)

            elif hostname:
                ctx.log('There is no record for hostname %s.', hostname)
                sys.exit(1)
