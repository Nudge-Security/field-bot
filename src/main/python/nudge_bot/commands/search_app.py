
import click

from nudge_bot.api import nudge, utility
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli


@cli.command(name='search-app',short_help="Search for an app")
@click.option('--app-name',     help='The app name')
@click.option('--domain',     help='The domain of the app')
@click.pass_obj
def list_fields(nudge_client:NudgeClient, app_name, domain):
    values = nudge_client.find_app(app_name)
    if len(values) == 0:
        click.secho(f"No apps found for name: {app_name} domain: {domain}",fg='red' )
    else:
        for value in values:
            click.secho(utility.print_app(value))


