

import click
from click import ClickException

from nudge_bot.api import nudge, utility
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli


@cli.command(name='bulk-set-app-field',short_help="Set a field for list of apps")
@click.option('--field',     help='The field to set', required=True)
@click.option('--value',     help='The value to set', required=True)
@click.option('--dry-run',     help='Just print the apps to be updated' , is_flag=True)
@click.option('--app-list',     help='A line delimited list of apps to set the field', type=click.File('r'), required=True)
@click.pass_obj
def list_fields(nudge_client:NudgeClient, field, value, app_list, dry_run):
    # do this to verify we can find the right field and value
    field_id, value_id = nudge_client.get_ids_for_field_and_value(field, value)
    apps_to_update ={}
    apps_not_found=[]
    for line in app_list.readlines():
        app_name = line.strip()
        apps = nudge_client.find_app(app_name=app_name, domain=None)
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
            index = click.prompt("Please input the number of the app you wish to set the field on: ", type=click.IntRange(1, count))
            app = apps[index]
        else:
            app = apps[0]
        if app:
            apps_to_update[app['id']] = app['service_info']['name']
    for id,name in apps_to_update.items():
        if dry_run:
            click.secho(f"Updating {name}: {id}")
        else:
            click.secho(f"Updating {name}: {id} to {field} : {value}")
            nudge_client.set_app_field(id, field, value)
    click.secho(f"Finished updating {len(apps_to_update)}")
    click.secho(f"Could not find {len(apps_not_found)} apps")
    for name in apps_not_found:
        click.secho(name,fg='red')