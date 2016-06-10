# -*- coding: utf-8 -*-
import sys
import click
import requests
import json
from ipamcli.cli import pass_context
from ipamcli.commands.tools import checkMAC, checkIP


@click.command('edit', short_help='edit exist entry in NOC')
@click.option('--ip', help='ip address of entry to be updated')
@click.option('--mac', help='mac address of entry to be updated')
@click.option('--task-id', help='task id of entry to be updated')
@click.option('--new-ip', help='new ip address for entry')
@click.option('--new-mac', help='new mac address for entry')
@click.option('--new-fqdn', help='new fqdn for entry')
@click.option('--new-description', help='new description for entry')
@click.option('--new-task-id', help='new task id for entry')
@pass_context
def cli(ctx, ip, mac, task_id, new_ip, new_mac, new_fqdn, new_description, new_task_id):
    """Edit entry information in NOC."""
    if ip:
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
        if len(resp) == 0:
            ctx.logerr('There is no record. For edit operation must be specified at least one entry.')
            sys.exit(1)

        elif len(resp) == 1:
            payload = dict()
            if new_ip:
                if not checkIP(new_ip):
                    ctx.logerr('IP adrress %s is invalid.', new_ip)
                    sys.exit(1)
                payload.update({'address': new_ip})

            if new_mac:
                if not checkMAC(new_mac):
                    ctx.logerr('MAC address %s is invalid.', mac)
                    sys.exit(1)
                payload.update({'mac': new_mac})

            if new_fqdn:
                payload.update({'fqdn': new_fqdn})

            if new_description:
                payload.update({'description': new_description})

            if new_task_id:
                payload.update({'tt': new_task_id})

            try:
                r = requests.put('{}/ip/address/{}/'.format(ctx.url, resp[0]['id']),
                                 auth=(ctx.username, ctx.password),
                                 data=json.dumps(payload))
            except:
                ctx.logerr('Oops. HTTP API error occured.')
                sys.exit(1)

            if r.status_code == 200:
                ctx.log('The entry has been successfully updated.')

            else:
                ctx.logerr('Error updating the entry.')
                sys.exit(1)

        else:
            ctx.logerr('There is multiple entries. For edit operation must be specified only one entry.')
            sys.exit(1)
