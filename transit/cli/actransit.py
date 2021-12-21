import json
import os
import click

from transit.modules.actransit import client

@click.group()
@click.option('--actransit-api-key', '-k')
@click.pass_context
def cli(ctx, actransit_api_key):
    ctx.obj['actransit_api_key'] = actransit_api_key or os.getenv('ACTRANSIT_API_KEY', None)

@cli.command()
@click.pass_context
def service_notices(ctx):
    resp = client.service_notices(ctx.obj['actransit_api_key'])
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.pass_context
def route_list(ctx):
    resp = client.route_list(ctx.obj['actransit_api_key'])
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.argument('route_name')
@click.pass_context
def route_directions(ctx, route_name):
    resp = client.route_directions(ctx.obj['actransit_api_key'], route_name)
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.option('--schedule', '-s', default='weekday')
@click.argument('route_name')
@click.argument('direction')
@click.pass_context
def route_trips(ctx, schedule, route_name, direction):
    resp = client.route_trips(ctx.obj['actransit_api_key'], route_name,
                              direction, schedule_type=schedule)
    click.echo(json.dumps(resp, indent=4))


@cli.command()
@click.argument('route_name')
@click.argument('trip_id')
@click.pass_context
def route_stops(ctx, route_name, trip_id):
    resp = client.route_stops(ctx.obj['actransit_api_key'], route_name, trip_id)
    click.echo(json.dumps(resp, indent=4))


@cli.command()
@click.argument('stop_id')
@click.pass_context
def stop_predictions(ctx, stop_id):
    resp = client.stop_predictions(ctx.obj['actransit_api_key'], stop_id)
    click.echo(json.dumps(resp, indent=4))

def main():
    cli(obj={}) #pylint:disable=no-value-for-parameter,unexpected-keyword-arg
