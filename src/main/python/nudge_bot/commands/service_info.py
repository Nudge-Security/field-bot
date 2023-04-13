import json

import click
from click import ClickException

from nudge_bot.api import nudge, utility
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.api.utility import ResolutionStatus
from nudge_bot.main import cli


@cli.command(name='app-info', short_help="App meta data search utility")
@click.option('--domain', help='The domain to find the app metadata for (domain or name)')
@click.pass_obj
def supply_chain(nudge_client: NudgeClient, domain):
    service_info = nudge_client.get_service_info(domain)
    click.secho(f"{domain}")
    click.secho(json.dumps(service_info, indent=2))
