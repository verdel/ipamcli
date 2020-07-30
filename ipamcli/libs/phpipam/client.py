# -*- coding: utf-8 -*-
import sys
import re
import requests
import netaddr
import json
from collections import OrderedDict
from ipamcli.libs.phpipam import exception

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


def in_dictlist(key, value, my_dictlist):
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


def get_token(ctx):
    try:
        r = requests.post('{}/user/'.format(ctx.url),
                          auth=(ctx.username, ctx.password))
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        return

    if r.status_code == 500:
        ctx.logerr(r.json()['message'])
        sys.exit(1)

    elif r.status_code == 200 and r.json():
        return r.json()['data']['token']

    else:
        return None


def get_network_mask_by_subnet(subnet):
    try:
        netmask = str(netaddr.IPNetwork(subnet).netmask)
    except Exception:
        return None
    return netmask


def get_subnet_id(ctx, network):
    try:
        r = requests.get('{}/subnets/cidr/{}'.format(ctx.url, str(network)),
                         headers={'token': ctx.token})
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        return None

    if r.status_code == 401:
        ctx.logerr('Wrong authorization token.')
        return None

    elif r.status_code == 200 and r.json():
        network_id = r.json()['data'][0]['id']

    return network_id


def get_subnet_by_id(ctx, subnetId):
    try:
        r = requests.get('{}/subnets/{}/'.format(ctx.url, str(subnetId)),
                         headers={'token': ctx.token})
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        return None

    if r.status_code == 401:
        ctx.logerr('Wrong authorization token.')
        return None

    elif r.status_code == 200 and r.json():
        subnet = r.json()['data']

    return subnet


def get_subnet_by_ip(ctx, ip):
    try:
        r = requests.get('{}/subnets/overlapping/{}/32'.format(ctx.url, str(ip)),
                         headers={'token': ctx.token})
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        return None

    if r.status_code == 401:
        ctx.logerr('Wrong authorization token.')
        return None

    elif r.status_code == 200 and r.json():
        subnet = r.json()['data'][0]

    return subnet


def get_addresses_from_subnet(ctx, subnet_id):
    try:
        r = requests.get('{}/subnets/{}/addresses/'.format(ctx.url, subnet_id),
                         headers={'token': ctx.token})
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        return None

    if r.status_code == 200 and r.json():
        return r.json()['data']
    else:
        return None


def get_network_prefix_by_subnet(subnet):
    try:
        prefix = str(netaddr.IPNetwork(subnet).prefixlen)
    except Exception:
        return None
    return prefix


def show_network_addresses(ctx, network, free_only, verbose):
    network_id = get_subnet_id(ctx, network)

    if network_id:
        network_set = netaddr.IPSet(network)

    else:
        if verbose:
            ctx.logerr('Subnet %s not found.', str(network))
        return False

    addresses = get_addresses_from_subnet(ctx, network_id)

    result = []
    network_set.remove(network.network)
    network_set.remove(network.broadcast)

    for item in network_set:
        phpipam_ip_info = in_dictlist('ip', str(item), addresses)
        if phpipam_ip_info:
            if not free_only:
                if phpipam_ip_info['description']:
                    phpipam_ip_info['description'] = phpipam_ip_info['description'].replace('\r\n', ' ')[:95]
                result.append(OrderedDict([
                                          ('Address', phpipam_ip_info['ip']),
                                          ('MAC', phpipam_ip_info['mac']),
                                          ('FQDN', phpipam_ip_info['hostname']),
                                          ('Description', phpipam_ip_info['description']),
                                          ('Task', phpipam_ip_info['custom_NOC_TT'])
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


def search_by_ip(ctx, ip):
    try:
        r = requests.get('{}/addresses/search/{}/'.format(ctx.url, ip),
                         headers={'token': ctx.token})
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        return None

    if r.status_code == 200 and r.json() and r.json()['success']:
        return r.json()['data']
    else:
        return None


def search_by_id(ctx, id):
    try:
        r = requests.get('{}/addresses/{}/'.format(ctx.url, id),
                         headers={'token': ctx.token})
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        return None

    if r.status_code == 200 and r.json() and r.json()['success']:
        return r.json()['data']
    else:
        return None


def remove_by_id(ctx, id):
    try:
        r = requests.delete('{}/addresses/{}/'.format(ctx.url, id),
                            headers={'token': ctx.token})
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        return None

    if r.status_code == 200 and r.json() and r.json()['success']:
        return True
    else:
        return None


def search_by_hostname(ctx, hostname):
    try:
        r = requests.get('{}/addresses/search_hostname/{}/'.format(ctx.url, hostname),
                         headers={'token': ctx.token})
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        return None

    if r.status_code == 200 and r.json() and r.json()['success']:
        return r.json()['data']
    else:
        return None


def get_first_empty(ctx, network):
    network_id = get_subnet_id(ctx, network)
    if network_id is None:
        return None

    try:
        r = requests.get('{}/subnets/{}/first_free/'.format(ctx.url, network_id),
                         headers={'token': ctx.token})
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        return None

    if r.status_code == 200 and r.json():
        ip = r.json()['data']
        return ip
    else:
        return None


def get_last_empty(ctx, network):
    network_id = get_subnet_id(ctx, network)
    if network_id:
        network_set = netaddr.IPSet(network)
    else:
        return None
    addresses = get_addresses_from_subnet(ctx, network_id)

    result = []
    network_set = netaddr.IPSet(network)
    network_set.remove(network.network)
    network_set.remove(network.broadcast)
    for item in network_set:
        ip_entry_exist = in_dictlist('ip', str(item), addresses)
        if not ip_entry_exist:
            result.append(item)

    return result[-1]


def add_address(ctx, payload):
    try:
        r = requests.post('{}/addresses/'.format(ctx.url),
                          headers={'Content-type': 'application/json', 'token': ctx.token},
                          data=json.dumps(payload))
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        return None

    if r.status_code == 201 and r.json() and r.json()['success']:
        return r.json()['id']
    elif r.status_code == 409 and r.json() and r.json()['message'] == 'IP address already exists':
        raise exception.ipamCLIIPExists
    else:
        return None


def edit_address(ctx, id, payload):
    try:
        r = requests.patch('{}/addresses/{}/'.format(ctx.url, id),
                           headers={'Content-type': 'application/json', 'token': ctx.token},
                           data=json.dumps(payload))
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        return None
    if r.status_code == 200 and r.json() and r.json()['success']:
        return True
    else:
        return None
