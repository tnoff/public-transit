import json

import click

from transit.modules.nextbus import client


@click.group()
def cli():
    pass

@cli.command()
def agency_list():
    resp = client.agency_list()
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.argument('agency_tag')
def route_list(agency_tag):
    resp = client.route_list(agency_tag)
    click.echo(json.dumps(resp, indent=4))


@cli.command()
@click.argument('agency_tag')
@click.argument('route_tag')
def route_show(agency_tag, route_tag):
    resp = client.route_show(agency_tag, route_tag)
    click.echo(json.dumps(resp, indent=4))


@cli.command()
@click.argument('agency_tag')
@click.argument('route_tag')
def route_messages(agency_tag, route_tag):
    resp = client.route_messages(agency_tag, route_tag)
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.argument('agency_tag')
@click.argument('stop_id')
def stop_prediction(agency_tag, stop_id):
    resp = client.stop_prediction(agency_tag, stop_id)
    click.echo(json.dumps(resp, indent=4))

def main():
    cli()
