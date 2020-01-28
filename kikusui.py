#!/usr/bin/env python3

import click
from yaml import safe_load
import visa
import os


APP_NAME = 'kikusui'


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


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


@click.command(cls=AliasedGroup)
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


@click.command()
@click.pass_context
def voltage(ctx):
    click.echo('%s' % ctx.obj['inst'].query('MEAS:VOLT?'))


@click.command()
@click.pass_context
def current(ctx):
    click.echo('%s' % ctx.obj['inst'].query('MEAS:VOLT?'))


cli.add_command(id)
cli.add_command(voltage)
cli.add_command(current)

if __name__ == '__main__':
    cli(obj={})
