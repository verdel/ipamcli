# -*- coding: utf-8 -*-
import click
import sys
from ipamcli.cli import pass_context
import ipamcli.libs.phpipam.client as phpipam


@click.command('remove', short_help='remove exist entry from phpIPAM')
@click.option('--id', help='id of entry to be deleted')
@click.option('--ip', help='ip address of entry to be deteled')
@pass_context
def cli(ctx, id, ip):
    """Remove entry from phpIPAM."""
    if id:
        try:
            result = phpipam.search_by_id(ctx, id)
        except Exception:
            ctx.logerr('Oops. HTTP API error occured.')
            sys.exit(1)

        if result is None:
            ctx.logerr('There is no entry for id %s.', id)
            sys.exit(1)

    elif ip:
        if not phpipam.checkIP(ip):
            ctx.logerr('IP address %s is invalid.', ip)
            sys.exit(1)
        try:
            address = phpipam.search_by_ip(ctx, ip)
        except Exception:
            ctx.logerr('Oops. HTTP API error occured.')
            sys.exit(1)

        if address is None:
            ctx.logerr('There is no entry for ip %s.', str(ip))
            sys.exit(1)
        else:
            id = address[0]['id']

    else:
        ctx.logerr('At least one of the remove option must be set.')
        sys.exit(1)

    try:
        result = phpipam.remove_by_id(ctx, id)
    except Exception:
        ctx.logerr('Oops. HTTP API error occured.')
        sys.exit(1)

    if result is not None:
        ctx.log('The entry has been successfully removed.')

    else:
        ctx.logerr('Error deleting entry.')
        sys.exit(1)
