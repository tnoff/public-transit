import json
import os
from pathlib import Path

import click
from dappertable import DapperTable, Column, Columns

from trip_planner.client import TripPlanner

DEFAULT_PATH = Path(os.path.expanduser('~')) / '.trip_planner'
DEFAULT_DB_PATH = DEFAULT_PATH / 'db.sql'

DEFAULT_PATH.mkdir(exist_ok=True)

def format_seconds(seconds: int) -> str:
    '''
    Format an arrival estimate as H:MM:SS, M:SS, or bare seconds
    '''
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f'{hours}:{minutes:02d}:{secs:02d}'
    if minutes:
        return f'{minutes}:{secs:02d}'
    return str(secs)

@click.group()
@click.option('--bart-api-key', '-bk', default='MW9S-E7SL-26DU-VV8V', envvar='BART_API_KEY')
@click.option('--actransit-api-key', '-ak', envvar='ACTRANSIT_API_KEY')
@click.option('--five11-api-key', '-fk', envvar='FIVE11_API_KEY')
@click.option('--database-file', '-db', default=str(DEFAULT_DB_PATH))
@click.pass_context
def cli(ctx, bart_api_key, actransit_api_key, five11_api_key, database_file):
    ctx.obj['actransit_api_key'] = actransit_api_key
    ctx.obj['bart_api_key'] = bart_api_key
    ctx.obj['five11_api_key'] = five11_api_key
    ctx.obj['client'] = TripPlanner(database_file,
                                    actransit_api_key=ctx.obj['actransit_api_key'],
                                    bart_api_key=ctx.obj['bart_api_key'],
                                    five11_api_key=ctx.obj['five11_api_key'])

@cli.command()
@click.pass_context
def leg_list(ctx):
    resp = ctx.obj['client'].leg_list()
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.argument('agency')
@click.argument('stop_id')
@click.option('--destinations', '-d', multiple=True, help='Only include destinations in output')
@click.pass_context
def leg_create(ctx, agency, stop_id, destinations):
    resp = ctx.obj['client'].leg_create(agency, stop_id, destinations)
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.argument('leg_id')
@click.pass_context
def leg_show(ctx, leg_id):
    agency, resp = ctx.obj['client'].leg_show(leg_id)
    click.echo(f'Agency {agency}')
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.argument('leg_id')
@click.pass_context
def leg_delete(ctx, leg_id):
    resp = ctx.obj['client'].leg_delete(leg_id)
    click.echo(resp)

@cli.command()
@click.argument('name')
@click.argument('legs', nargs=-1)
@click.pass_context
def trip_create(ctx, name, legs):
    resp = ctx.obj['client'].trip_create(name, legs)
    click.echo(resp)

@cli.command()
@click.pass_context
def trip_list(ctx):
    resp = ctx.obj['client'].trip_list()
    click.echo(json.dumps(resp, indent=4))

@cli.command()
@click.argument('trip_id')
@click.pass_context
def trip_show(ctx, trip_id):
    resp = ctx.obj['client'].trip_show(trip_id)
    for agency, agency_data in resp.items():
        if not agency_data:
            continue
        print(f'Agency {agency}')
        table = DapperTable(columns=Columns([
            Column('Stop', 24),
            Column('Destination', 34),
            Column('Times (H:MM:SS)', 46),
        ]))
        for stop, estimate_data in agency_data.items():
            for dest_name, est_times in estimate_data.items():
                times = ", ".join(format_seconds(e) for e in est_times)
                table.add_row([stop, dest_name, times])
        print(table.render())
        print()

@cli.command()
@click.argument('trip_id')
@click.pass_context
def trip_delete(ctx, trip_id):
    resp = ctx.obj['client'].trip_delete(trip_id)
    click.echo(resp)

def main():
    cli(obj={}) #pylint:disable=no-value-for-parameter,unexpected-keyword-arg
