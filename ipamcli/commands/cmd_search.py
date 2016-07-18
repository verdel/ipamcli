# -*- coding: utf-8 -*-
import sys
import click
import netaddr
import requests
from ipamcli.cli import pass_context
from ipamcli.commands.tools import VLANS, checkMAC, checkIP, get_network_prefix_by_id, get_network_description_by_id, get_first_empty


@click.command('search', short_help='search entry in NOC')
@click.option('--ip', help='ip address of entry to search')
@click.option('--mac', help='mac address of entry to search')
@click.option('--contains', is_flag=True, help='search not only complete but also partial matches')
@click.option('--task-id', metavar='<int>', help='task id of entry to search')
@click.option('--first-empty', is_flag=True, help='search first empty IP address')
@click.option('--network', help='network address for first-empty search')
@click.option('--vlan-id', metavar='<int>', help='vlan id for first-empty search')
@click.option('--vlan-name', help='vlan name for first-empty search')
@pass_context
def cli(ctx, ip, mac, contains, task_id, first_empty, network, vlan_id, vlan_name):
    """Search entry information in NOC."""
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

        if not get_first_empty(ctx, network, verbose=True):
            sys.exit(1)

    else:
        if ip and not contains:
            if not checkIP(ip):
                ctx.logerr('IP address %s is invalid.', ip)
                sys.exit(1)

            try:
                r = requests.get('{}/ip/address/'.format(ctx.url),
                                 auth=(ctx.username, ctx.password),
                                 params={'address': ip})
            except:
                ctx.logerr('Oops. HTTP API error occured.')
                sys.exit(1)

        elif ip:
            try:
                r = requests.get('{}/ip/address/'.format(ctx.url),
                                 auth=(ctx.username, ctx.password),
                                 params={'address__contains': ip})
            except:
                ctx.logerr('Oops. HTTP API error occured.')
                sys.exit(1)

        elif mac:
            if not checkMAC(mac):
                ctx.logerr('MAC address %s is invalid.', mac)
                sys.exit(1)

            else:
                try:
                    r = requests.get('{}/ip/address/'.format(ctx.url),
                                     auth=(ctx.username, ctx.password),
                                     params={'mac': mac})
                except:
                    ctx.logerr('Oops. HTTP API error occured.')
                    sys.exit(1)

        elif task_id:
            try:
                r = requests.get('{}/ip/address/'.format(ctx.url),
                                 auth=(ctx.username, ctx.password),
                                 params={'tt': task_id})
            except:
                ctx.logerr('Oops. HTTP API error occured.')
                sys.exit(1)

        else:
            ctx.logerr('At least one of the search option must be set.')
            sys.exit(1)

        if r.status_code == 403:
            ctx.logerr('Invalid username or password.')
            sys.exit(1)

        else:
            resp = r.json()
            if resp:
                resp = sorted(resp, key=lambda k: netaddr.IPAddress(k['address']))
                for item in resp:
                    ctx.log(u'ID: %s\nSubnet prefix: %s\nSubnet description: %s\nIP: %s\nMAC: %s\nFQDN: %s\nDescription: %s\nID заявки: %s\n',
                            item['id'],
                            get_network_prefix_by_id(ctx, item['prefix']),
                            get_network_description_by_id(ctx, item['prefix']),
                            item['address'],
                            item['mac'],
                            item['fqdn'],
                            item['description'],
                            item['tt'])

            else:
                if ip:
                    ctx.log('There is no record for ip address %s.', ip)
                    sys.exit(1)

                elif mac:
                    ctx.log('There is no record for mac address %s.', mac)
                    sys.exit(1)

                elif task_id:
                    ctx.log(u'There is no record for ID заявки %s.', task_id)
                    sys.exit(1)
