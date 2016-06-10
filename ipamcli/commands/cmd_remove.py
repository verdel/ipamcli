# -*- coding: utf-8 -*-
import click
import requests
import sys
from ipamcli.cli import pass_context
from ipamcli.commands.tools import checkMAC, checkIP


@click.command('remove', short_help='remove exist entry from NOC')
@click.option('--id', help='id of entry to be deleted')
@click.option('--ip', help='ip address of entry to be deteled')
@click.option('--mac', help='mac address of entry to be deleted')
@pass_context
def cli(ctx, id, ip, mac):
    """Remove entry from NOC."""
    if id:
        try:
            r = requests.get('{}/ip/address/'.format(ctx.url),
                             auth=(ctx.username, ctx.password),
                             params={'id': id})
        except:
            ctx.logerr('Oops. HTTP API error occured.')
            sys.exit(1)

        if r.status_code == 403:
            ctx.logerr('Invalid username or password.')
            sys.exit(1)

        elif r.status_code != 200 or not r.json():
            ctx.logerr('There is no entry for id %s.', id)
            sys.exit(1)

    elif ip:
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

        if r.status_code == 403:
            ctx.logerr('Invalid username or password.')
            sys.exit(1)

        elif r.status_code != 200 or not r.json():
            ctx.logerr('There is no entry for ip %s.', str(ip))
            sys.exit(1)

        else:
            id = r.json()[0]['id']

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

            if r.status_code == 403:
                ctx.logerr('Invalid username or password.')
                sys.exit(1)

            elif r.status_code != 200 or not r.json():
                ctx.logerr('There is no entry for mac %s.', mac)
                sys.exit(1)

            elif len(r.json()) == 1:
                    id = r.json()[0]['id']

            else:
                ctx.logerr('There is multiple entry for MAC %s. For a remove operation must be specified only one entry.', mac)
                sys.exit(1)

    else:
        ctx.logerr('At least one of the remove option must be set.')
        sys.exit(1)

    try:
        r = requests.delete('{}/ip/address/{}'.format(ctx.url, id),
                            auth=(ctx.username, ctx.password))
    except:
        ctx.logerr('Oops. HTTP API error occured.')
        sys.exit(1)

    if r.status_code == 403:
        ctx.logerr('Invalid username or password.')
        sys.exit(1)

    elif r.status_code == 204:
        ctx.log('The entry has been successfully removed.')

    else:
        ctx.logerr('Error deleting entry.')
        sys.exit(1)
