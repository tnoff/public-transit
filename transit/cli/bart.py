import json

import click

from transit.modules.bart import client

@click.group()
@click.option('--bart-api-key', '-k', default='MW9S-E7SL-26DU-VV8V')
@click.pass_context
def cli(ctx, bart_api_key):
    ctx.obj['bart_api_key'] = bart_api_key

@cli.command()
@click.pass_context
def service_advisory(ctx):
    resp = client.service_advisory(ctx.obj['bart_api_key'])
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.pass_context
def train_count(ctx):
    resp = client.train_count(ctx.obj['bart_api_key'])
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.pass_context
def elevator_status(ctx):
    resp = client.elevator_status(ctx.obj['bart_api_key'])
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.pass_context
def station_list(ctx):
    resp = client.station_list(ctx.obj['bart_api_key'])
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.option('--platform', '-p')
@click.option('--direction', '-d')
@click.argument('origin')
@click.pass_context
def station_departures(ctx, platform, direction, origin):
    resp = client.station_departures(ctx.obj['bart_api_key'], origin,
                                     platform=platform, direction=direction)
    click.echo(json.dumps(resp, indent=4))

def main():
    cli(obj={}) #pylint:disable=no-value-for-parameter,unexpected-keyword-arg
