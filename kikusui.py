#!/usr/bin/env python3

import click
from yaml import safe_load
import visa
import os


APP_NAME = 'kikusui'


def get_ipaddr_from_config():
    cfg_file = os.path.join(click.get_app_dir(APP_NAME), 'config.yml')
    try:
        with click.open_file(cfg_file, 'r') as stream:
            try:
                cfg = safe_load(stream)
                ipaddr = cfg['ip']
            except yaml.YAMLError:
                click.echo("Oops", err=True)
    except FileNotFoundError:
        click.echo(f"Create {cfg} and try again", err=True)
        raise

    return ipaddr


@click.group()
@click.option('--ipaddr', help='IP address to connect to.')
@click.pass_context
def cli(ctx, ipaddr):
    if not ipaddr:
        ipaddr = get_ipaddr_from_config()
    rm = visa.ResourceManager('@py')
    inst = rm.open_resource(f'TCPIP0::{ipaddr}::5025::SOCKET')
    inst.read_termination = '\n'
    inst.write_termination = '\n'

    ctx.obj['inst'] = inst

    pass


@click.command()
@click.pass_context
def id(ctx):
    click.echo('%s' % ctx.obj['inst'].query('*IDN?'))


cli.add_command(id)

if __name__ == '__main__':
    cli(obj={})
