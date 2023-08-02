# -*- coding: utf-8 -*-
import sys
import click
from ipamcli.cli import pass_context
import ipamcli.libs.phpipam.client as phpipam


@click.command('edit', short_help='edit exist entry in phpIPAM')
@click.option('--ip', help='ip address of entry to be updated')
@click.option('--new-mac', help='new mac address for entry')
@click.option('--new-hostname', help='new fqdn for entry')
@click.option('--new-description', help='new description for entry')
@pass_context
def cli(ctx, ip, new_mac, new_hostname, new_description):
    """Edit entry information in phpIPAM."""
    if ip:
        if not phpipam.checkIP(ip):
            ctx.logerr('IP address %s is invalid.', ip)
            sys.exit(1)

        try:
            resp = phpipam.search_by_ip(ctx, ip)
        except Exception:
            ctx.logerr('Oops. HTTP API error occured.')
            sys.exit(1)

        if resp:
            payload = dict()
            if new_mac:
                if not phpipam.checkMAC(new_mac):
                    ctx.logerr('MAC address %s is invalid.', new_mac)
                    sys.exit(1)
                payload.update({'mac': new_mac})

            if new_hostname:
                payload.update({'hostname': new_hostname})

            if new_description:
                payload.update({'description': new_description})

            try:
                result = phpipam.edit_address(ctx, resp[0]['id'], payload)
            except Exception:
                ctx.logerr('Oops. HTTP API error occured.')
                sys.exit(1)

            if result is not None:
                ctx.log('The entry has been successfully edit.')
            else:
                ctx.logerr('Error editing entry.')
                sys.exit(1)

        else:
            ctx.logerr('There is no entry with ip %s.', ip)
            sys.exit(1)
