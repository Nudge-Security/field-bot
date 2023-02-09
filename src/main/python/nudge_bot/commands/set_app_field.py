
import click
from click import ClickException

from nudge_bot.api import nudge, utility
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli


@cli.command(name='set-app-field',short_help="Set a field for a given app")

@click.option('--field',     help='The field to set')
@click.option('--value',     help='The value to set')
@click.option('--app-name',     help='The name of the app to set the field on')
@click.option('--domain',     help='The domain of the app to set the field on')
@click.pass_obj
def list_fields(nudge_client:NudgeClient, field, value, app_name, domain):
    apps = nudge_client.find_app(app_name,domain)
    app_id = None
    if len(apps) == 0:
        click.secho(f"No apps found for name: {app_name} domain: {domain}")
    elif len(apps) == 1:
        app = apps[0]
        click.confirm(f"We found one app - is this right? {utility.print_app(app)}",abort=True )
        app_id = app['id']
    elif len(apps) >10:
        raise ClickException(f"We found {len(apps)} please narrow down your search parameters")
    else:
        count = 0
        for app in apps:
            count +=1
            click.secho(f"{count}. {utility.print_app(app)}")
        value = click.prompt("Please input the number of the app you wish to set the field on: ",
                              type=click.IntRange(1, count))
        app_id = apps[value]['id']
    nudge_client.set_app_field(app_id, field, value)


