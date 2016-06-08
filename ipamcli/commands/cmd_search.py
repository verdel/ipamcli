# -*- coding: utf-8 -*-
import click
import netaddr
import requests
from ipamcli.cli import pass_context
from ipamcli.commands.tools import VLANS, checkMAC, checkIP, get_network_by_id, get_first_empty


@click.command('search', short_help='search entry in NOC')
@click.option('--ip', help='ip address of entry to search')
@click.option('--mac', help='mac address of entry to search')
@click.option('--contains', is_flag=True, help='search not only complete but also partial matches')
@click.option('--task-id', metavar='INT', help='task id of entry to search')
@click.option('--first-empty', is_flag=True, help='search first empty IP address')
@click.option('--network', help='network address for first-empty search')
@click.option('--vlan-id', metavar='INT', help='vlan id for first-empty search')
@click.option('--vlan-name', help='vlan name for first-empty search')
@pass_context
def cli(ctx, ip, mac, contains, task_id, first_empty, network, vlan_id, vlan_name):
    """Search entry information in NOC."""
    if first_empty:
        if not network and not vlan_id and not vlan_name:
            ctx.logerr('At least one of the --network / --vlan-id / --vlan-name option must be set when use --first-empty option.')
            return

        if vlan_id:
            if vlan_id not in VLANS:
                ctx.logerr('No such vlan id in list.')
                return

            else:
                network = VLANS[vlan_id]['prefix']

        elif vlan_name:
            for item in VLANS:
                if VLANS[item]['name'] == vlan_name:
                    network = VLANS[item]['prefix']

            if not network:
                ctx.logerr('No such vlan name in list.')
                return

        try:
            network = netaddr.IPNetwork(network)

        except netaddr.core.AddrFormatError:
            ctx.logerr('Network address %s is invalid.', network)
            return

        if not get_first_empty(ctx, network, verbose=True):
            return

    else:
        if ip and not contains:
            if not checkIP(ip):
                ctx.logerr('IP address %s is invalid.', ip)
                return

            try:
                r = requests.get('{}/ip/address/'.format(ctx.url),
                                 auth=(ctx.username, ctx.password),
                                 params={'address': ip})
            except:
                ctx.logerr('Oops. HTTP API error occured.')
                return

        elif ip:
            try:
                r = requests.get('{}/ip/address/'.format(ctx.url),
                                 auth=(ctx.username, ctx.password),
                                 params={'address__contains': ip})
            except:
                ctx.logerr('Oops. HTTP API error occured.')
                return

        elif mac:
            if not checkMAC(mac):
                ctx.logerr('MAC address %s is invalid.', mac)
                return

            else:
                try:
                    r = requests.get('{}/ip/address/'.format(ctx.url),
                                     auth=(ctx.username, ctx.password),
                                     params={'mac': mac})
                except:
                    ctx.logerr('Oops. HTTP API error occured.')
                    return

        elif task_id:
            try:
                r = requests.get('{}/ip/address/'.format(ctx.url),
                                 auth=(ctx.username, ctx.password),
                                 params={'tt__contains': task_id})
            except:
                ctx.logerr('Oops. HTTP API error occured.')
                return

        else:
            ctx.logerr('At least one of the search option must be set.')
            return

        if r.status_code == 403:
            ctx.logerr('Invalid username or password.')
            return

        else:
            resp = r.json()
            if resp:
                resp = sorted(resp, key=lambda k: netaddr.IPAddress(k['address']))
                for item in resp:
                    ctx.log(u'ID: %s\nSubnet: %s\nIP: %s\nMAC: %s\nFQDN: %s\nDescription: %s\nID заявки: %s\n',
                            item['id'],
                            get_network_by_id(ctx, item['prefix']),
                            item['address'],
                            item['mac'],
                            item['fqdn'],
                            item['description'],
                            item['tt'])

            else:
                if ip:
                    ctx.log('There is no record for ip address %s.', ip)

                elif mac:
                    ctx.log('There is no record for mac address %s.', mac)

                elif task_id:
                    ctx.log(u'There is no record for ID заявки %s.', task_id)
