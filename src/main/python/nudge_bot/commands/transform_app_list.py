

import click
from click import ClickException

from nudge_bot.api import nudge, utility
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli


@cli.command(name='transform-app-list',short_help="Transform list of app names or domains to internal identifier")
@click.option('--app-list',     help='A line delimited list of apps to set the field', type=click.File('r'), required=True)
@click.option('--transformed-list',     help='The file to write the transformed list', type=click.File('w'), default="transformed_list.txt")
@click.pass_obj
def transform_app_list(nudge_client:NudgeClient, app_list, transformed_list):
    # do this to verify we can find the right field and value
    apps_to_update ={}
    apps_not_found=[]
    for line in app_list.readlines():
        app_name = line.strip()
        apps = nudge_client.find_app(app_name=app_name)
        app = None
        if not apps or len(apps) == 0:
            click.secho(f"Unable to find app {app_name}", fg='red')
            apps_not_found.append(app_name)
            continue
        if len(apps)>1:
            click.secho(f"Found ambiguous app name {app_name}", fg='red')
            count = 0
            for app in apps:
                count +=1
                click.secho(f"{count}. {utility.print_app(app)}")
            index = click.prompt("Please input the number of the app you wish to select: ", type=click.IntRange(1, count))
            app = apps[index-1]
        else:
            app = apps[0]
        if app:
            apps_to_update[app['id']] = app['service_info']['name']
    click.secho(f"Transformed {len(apps_to_update)} apps, writing to disk", fg='green')
    for id,name in apps_to_update.items():
        transformed_list.writelines(f"{id}\n")
    click.secho(f"Failed to transform {len(apps_not_found)} apps", fg='red')
    for name in apps_not_found:
        click.secho(f"\t{name}")