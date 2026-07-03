import json
import os
import click

from transit.modules.five11 import client

@click.group()
@click.option('--five11-api-key', '-k')
@click.pass_context
def cli(ctx, five11_api_key):
    ctx.obj['five11_api_key'] = five11_api_key or os.getenv('FIVE11_API_KEY', None)

@cli.command()
@click.pass_context
def operators(ctx):
    resp = client.operators(ctx.obj['five11_api_key'])
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.argument('operator')
@click.pass_context
def lines(ctx, operator):
    resp = client.lines(ctx.obj['five11_api_key'], operator)
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.argument('operator')
@click.option('--line', '-l', help='Filter to a single line id (from `five11 lines`)')
@click.pass_context
def stops(ctx, operator, line):
    resp = client.stops(ctx.obj['five11_api_key'], operator, line_id=line)
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.argument('operator')
@click.argument('stop_code', required=False)
@click.pass_context
def stop_monitoring(ctx, operator, stop_code):
    resp = client.stop_monitoring(ctx.obj['five11_api_key'], operator, stop_code)
    click.echo(json.dumps(resp, indent=4))

def main():
    cli(obj={}) #pylint:disable=no-value-for-parameter,unexpected-keyword-arg
