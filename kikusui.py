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
    cfg_dirs = [os.getcwd(), click.get_app_dir(APP_NAME)]
    for cfg_dir in cfg_dirs:
        cfg_file = os.path.join(cfg_dir, 'config.yml')
        try:
            with click.open_file(cfg_file, 'r') as stream:
                try:
                    cfg = safe_load(stream)
                    ipaddr = cfg['ip']
                    return ipaddr
                except yaml.YAMLError:
                    click.echo("Oops", err=True)
        except FileNotFoundError:
            continue

    dirs = ' or '.join(cfg_dirs)
    raise Exception(f'"config.yml" not found in either {dirs}')


@click.command(cls=AliasedGroup, context_settings=dict(help_option_names=["-h", "--help"]))
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
def measure(ctx):
    outp = ctx.obj['inst'].query('OUTP?')
    mvolt = float(ctx.obj['inst'].query('MEAS:VOLT?'))
    mcurr = float(ctx.obj['inst'].query('MEAS:CURR?'))
    volt = float(ctx.obj['inst'].query('VOLT?'))
    curr = float(ctx.obj['inst'].query('CURR?'))
    ovp = float(ctx.obj['inst'].query('VOLT:PROT?'))
    ocp = float(ctx.obj['inst'].query('CURR:PROT?'))
    click.echo('out %s' % ('yes' if outp == '1' else 'no'))
    click.echo(f'voltage {mvolt} V / {volt} V / {ovp} V')
    click.echo(f'current {mcurr} A / {curr} A / {ocp} A')


@click.command()
@click.pass_context
@click.option('-s', '--set', type=float)
def voltage(ctx, set):
    if set:
        ctx.obj['inst'].write(f'VOLT {set}')
    else:
        click.echo('%s' % float(ctx.obj['inst'].query('VOLT?')))


@click.command()
@click.pass_context
def current(ctx):
    click.echo('%s' % float(ctx.obj['inst'].query('CURR?')))


@click.command()
@click.pass_context
@click.option('-s', '--set', type=click.IntRange(0, 1))
def output(ctx, set):
    if set == None:
        click.echo('%s' % ctx.obj['inst'].query('OUTP?'))
    else:
        ctx.obj['inst'].write(f'OUTP {set}')


@click.command()
@click.pass_context
@click.option('-s', '--set', type=float)
def ovp(ctx, set):
    if set:
        ctx.obj['inst'].write(f'VOLT:PROT {set}')
    else:
        click.echo('%s' % float(ctx.obj['inst'].query('VOLT:PROT?')))


@click.command()
@click.pass_context
@click.option('-s', '--set', type=float)
def ocp(ctx, set):
    if set:
        ctx.obj['inst'].write(f'CURR:PROT {set}')
    else:
        click.echo('%s' % float(ctx.obj['inst'].query('CURR:PROT?')))


cli.add_command(id)
cli.add_command(measure)
cli.add_command(voltage)
cli.add_command(current)
cli.add_command(output)
cli.add_command(ovp)
cli.add_command(ocp)

if __name__ == '__main__':
    cli(obj={})
