# -*- coding: utf-8 -*-
import sys
import re
import requests
import netaddr
import json
from collections import OrderedDict
from ipamcli.libs.phpipam import exception


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
                                          ('Description', phpipam_ip_info['description'])
                                          ]))
        else:
            result.append(OrderedDict([
                                      ('Address', str(item)),
                                      ('MAC', ''),
                                      ('FQDN', ''),
                                      ('Description', 'free'),
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
