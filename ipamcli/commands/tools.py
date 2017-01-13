# -*- coding: utf-8 -*-
import sys
import re
import requests
import netaddr
from collections import OrderedDict

VLANS = {'22': {'name': 'smev-vipnet-vlan', 'prefix': '10.32.250.0/24'},
         '23': {'name': 'uek-vlan', 'prefix': '10.38.33.72/29'},
         '24': {'name': 'lpu-vlan', 'prefix': '10.33.80.0/24'},
         '25': {'name': 'obr-vipnet-vlan', 'prefix': '91.227.95.96/29'},
         '26': {'name': 'minzdrav-vipnet-vlan', 'prefix': '91.227.95.112/29'},
         '27': {'name': 'crpsec-vipnet-vlan', 'prefix': '10.32.252.0/24'},
         '28': {'name': 'crprmt-vipnet-vlan', 'prefix': '10.33.76.0/24'},
         '29': {'name': 'sooz-vipnet-vlan', 'prefix': '10.32.253.0/24'},
         '33': {'name': 'dragnet-vipnet-vlan', 'prefix': '10.33.72.0/24'},
         '34': {'name': 'zastava-vipnet-vlan', 'prefix': '10.11.26.0/24'},
         '54': {'name': 'users-vlan', 'prefix': '172.17.0.0/16'},
         '55': {'name': 'voip-vlan', 'prefix': '10.32.8.0/22'},
         '100': {'name': 'dmz-rt-vlan', 'prefix': '91.227.94.0/25'},
         '102': {'name': 'yb-vpn-vlan', 'prefix': '10.32.14.116/30'},
         '201': {'name': 'dmz-vlan', 'prefix': '91.227.93.0/24'},
         '203': {'name': 'mgmt-vlan', 'prefix': '10.33.16.0/20'},
         '205': {'name': 'infr-vlan', 'prefix': '10.33.64.0/23'},
         '206': {'name': 'is-vlan', 'prefix': '10.33.68.0/22'},
         '213': {'name': 'azk-vlan', 'prefix': '10.33.66.0/24'},
         '219': {'name': 'saperion-vlan', 'prefix': '10.32.14.112/30'},
         '221': {'name': 'yb-mgmt-vlan', 'prefix': '10.46.77.0/24'},
         '222': {'name': 'vks-vlan', 'prefix': '91.227.94.144/28'},
         '223': {'name': 'nessus-vlan', 'prefix': '91.227.94.144/28'},
         '224': {'name': 'ex-vlan', 'prefix': '10.33.60.0/24'},
         '226': {'name': 'jkh-vlan', 'prefix': '10.33.7.32/27'},
         '897': {'name': 'jdoc-db-vlan', 'prefix': '10.38.200.0/24'}
         }


def in_dictlist((key, value), my_dictlist):
    for this in my_dictlist:
        if this[key] == value:
            return this
    return {}


def checkIP(ip):
    a = ip.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return netaddr.IPAddress(ip)


def checkMAC(mac):
    if re.match('[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$',
                mac.lower()):
        return True
    else:
        return False


def get_network_prefix_by_id(ctx, id):
    try:
        r = requests.get('{}/ip/prefix/'.format(ctx.url),
                         auth=(ctx.username, ctx.password),
                         params={'id': id})
    except:
        ctx.logerr('Oops. HTTP API error occured.')
        return

    if r.status_code == 403:
        ctx.logerr('Invalid username or password.')
        sys.exit(1)

    elif r.status_code == 200 and r.json():
        return r.json()[0]['prefix']

    else:
        return None


def get_network_description_by_id(ctx, id):
    try:
        r = requests.get('{}/ip/prefix/'.format(ctx.url),
                         auth=(ctx.username, ctx.password),
                         params={'id': id})
    except:
        ctx.logerr('Oops. HTTP API error occured.')
        return

    if r.status_code == 403:
        ctx.logerr('Invalid username or password.')
        sys.exit(1)

    elif r.status_code == 200 and r.json():
        return r.json()[0]['description']

    else:
        return None


def show_network_addresses(ctx, network, free_only, verbose):
    try:
        r = requests.get('{}/ip/prefix/'.format(ctx.url),
                         auth=(ctx.username, ctx.password),
                         params={'prefix': str(network)})
    except:
        ctx.logerr('Oops. HTTP API error occured.')
        sys.exit(1)

    if r.status_code == 403:
        ctx.logerr('Invalid username or password.')
        sys.exit(1)

    elif r.status_code == 200 and r.json():
        network_id = r.json()[0]['id']
        network_set = netaddr.IPSet(network)

    else:
        if verbose:
            ctx.logerr('Subnet %s not found.', str(network))
        return False

    try:
        r = requests.get('{}/ip/address/'.format(ctx.url),
                         auth=(ctx.username, ctx.password),
                         params={'prefix': network_id})
    except:
        ctx.logerr('Oops. HTTP API error occured.')
        return

    result = []

    if r.status_code == 200 and r.json():
        network_set.remove(network.network)
        network_set.remove(network.broadcast)
        for item in network_set:
            noc_ip_info = in_dictlist(('address', str(item)), r.json())
            if noc_ip_info:
                if not free_only:
                    result.append(OrderedDict([
                                              ('Address', noc_ip_info['address']),
                                              ('MAC', noc_ip_info['mac']),
                                              ('FQDN', noc_ip_info['fqdn']),
                                              ('Description', noc_ip_info['description'].replace('\r\n', ' ')[:95]),
                                              ('Task', noc_ip_info['tt'])
                                              ]))
            else:
                result.append(OrderedDict([
                                          ('Address', str(item)),
                                          ('MAC', ''),
                                          ('FQDN', ''),
                                          ('Description', 'free'),
                                          ('Task', '')
                                          ]))
    return result


def get_first_empty(ctx, network, reverse, verbose):
    try:
        r = requests.get('{}/ip/prefix/'.format(ctx.url),
                         auth=(ctx.username, ctx.password),
                         params={'prefix': str(network)})
    except:
        ctx.logerr('Oops. HTTP API error occured.')
        return

    if r.status_code == 403:
        ctx.logerr('Invalid username or password.')
        sys.exit(1)

    elif r.status_code == 200 and r.json():
        network_id = r.json()[0]['id']
        network_set = netaddr.IPSet(network)

    else:
        if verbose:
            ctx.logerr('Subnet %s not found.', str(network))
        return False

    try:
        r = requests.get('{}/ip/address/'.format(ctx.url),
                         auth=(ctx.username, ctx.password),
                         params={'prefix': network_id})
    except:
        ctx.logerr('Oops. HTTP API error occured.')
        return

    if r.status_code == 200 and r.json():
        network_set.remove(network.network)
        network_set.remove(network.broadcast)
        for item in r.json():
            network_set.remove(item['address'])

        if not reverse:
            ip = network_set.__iter__().next()
        else:
            for ip in network_set:
                pass
        if verbose:
            ctx.log('First empty IP address in subnet %s:\n%s',
                    str(network), str(ip))
        return str(ip)
