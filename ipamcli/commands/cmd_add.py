# -*- coding: utf-8 -*-
import click
import netaddr
import sys
from ipamcli.cli import pass_context
import ipamcli.libs.phpipam.client as phpipam
from ipamcli.libs.phpipam import exception


@click.command('add', short_help='add new entry to phpIPAM')
@click.option('--first-empty', is_flag=True, help='search first empty IP address')
@click.option('--last-empty', is_flag=True, help='search last empty IP address')
@click.option('--network', help='network address for first-empty search')
@click.option('--vlan-id', metavar='<int>', help='vlan id for first-empty search')
@click.option('--vlan-name', help='vlan name for first-empty search')
@click.option('--ip', help='ip address for new entry')
@click.option('--mac', help='mac address for new entry')
@click.option('--hostname', default='fqdn.local', show_default=True, help='fqdn for new entry')
@click.option('--description', default="", help='description for new entry')
@pass_context
def cli(ctx, first_empty, last_empty, network, vlan_id, vlan_name, ip, mac, hostname, description):
    """Add new entry to phpIPAM."""
    if first_empty or last_empty:
        if not network and not vlan_id and not vlan_name:
            ctx.logerr('At least one of the --network / --vlan-id / --vlan-name option must be set when use --first-empty / --last-empty option .')
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

        subnetId = phpipam.get_subnet_id(ctx, network)

        if first_empty:
            ip = phpipam.get_first_empty(ctx, network)
        elif last_empty:
            ip = phpipam.get_last_empty(ctx, network)

        if ip is None:
            ctx.logerr('No free IP found in subnet.')
            sys.exit(1)

    elif ip:
        if not phpipam.checkIP(ip):
            ctx.logerr('IP address %s is invalid.', ip)
            sys.exit(1)
        else:
            subnet = phpipam.get_subnet_by_ip(ctx, ip)
            subnetId = subnet['id']
            network = subnet['subnet']
            try:
                network = netaddr.IPNetwork(network)

            except netaddr.core.AddrFormatError:
                ctx.logerr('Network address %s is invalid.', network)
                sys.exit(1)

    else:
        ctx.logerr('At least one of the add option must be set.')
        sys.exit(1)

    if mac:
        if not phpipam.checkMAC(mac):
            ctx.logerr('MAC address %s is invalid.', mac)
            return
    else:
        mac = ""

    payload = {"subnetId": int(subnetId), "ip": str(ip), "mac": mac, "hostname": hostname, "description": description}
    try:
        result = phpipam.add_address(ctx, payload)

    except exception.ipamCLIIPExists:
        ctx.logerr('Oops. IP address already exists.')
        sys.exit(1)

    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        sys.exit(1)

    if result is not None:
        ctx.log('The entry for ip %s/%s (%s) has been successfully created. The entry ID: %s.',
                ip,
                phpipam.get_network_prefix_by_subnet(network),
                phpipam.get_network_mask_by_subnet(network),
                result)

    else:
        ctx.logerr('Error creating entry.')
        sys.exit(1)
