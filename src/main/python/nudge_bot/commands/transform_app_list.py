from typing import List

import click
from click import ClickException, progressbar

from nudge_bot.api import nudge, utility
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.api.utility import ResolutionStatus, AppResolution, AppResolutionCollection
from nudge_bot.main import cli


@cli.command(name='transform-app-list',short_help="Transform list of app names or domains to internal identifier")
@click.option('--app-list',     help='A line delimited list of apps to set the field', type=click.File('r'), required=True)
@click.option('--interactive',     help='Choose to resolve interactively', is_flag=True,default=False)
@click.option('--transformed-list',     help='The file to write the transformed list', type=click.File('w'), default="transformed_list.txt")
@click.pass_obj
def transform_app_list(nudge_client:NudgeClient, app_list, transformed_list, interactive):
    # do this to verify we can find the right field and value
    results = AppResolutionCollection()
    with progressbar(app_list.readlines()) as readlines:
        for line in readlines:
            meta = line.split(',')
            app_name = meta[0].strip()
            value = None
            if len(meta) > 1:
                if len(meta) >2:
                    raise ClickException(f"Extraneous comma in line {line}")
                value = meta[1].strip()
            app_resolution = utility.resolve_app(app_name, nudge_client=nudge_client,interactive=interactive)
            if value:
                app_resolution.add_meta_data(value)
            results.add(app_resolution)

    click.secho(f"Transformed {results.count(ResolutionStatus.RESOLVED)} apps, writing to disk", fg='green')
    for app_resolution in results.get(ResolutionStatus.RESOLVED):
        transformed_list.writelines(f"{app_resolution.print()}\n")
        click.secho(f"\t{app_resolution.print_app_name()}",fg='green')
    if results.count(ResolutionStatus.NOT_FOUND)>0:
        click.secho(f"Failed to find {results.count(ResolutionStatus.NOT_FOUND)} apps", fg='red')
        for app_resolution in results.get(ResolutionStatus.NOT_FOUND):
            click.secho(f"\t{app_resolution.print()}")
    if results.count(ResolutionStatus.AMBIGUOUS) >0:
        click.secho(f"Failed to reliably identify {results.count(ResolutionStatus.AMBIGUOUS)} apps", fg='red')
        for app_resolution in results.get(ResolutionStatus.AMBIGUOUS):
            click.secho(f"\t{app_resolution.print()}")
