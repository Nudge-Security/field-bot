
import click
from click import ClickException

from nudge_bot.api import nudge, utility
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.api.utility import ResolutionStatus
from nudge_bot.main import cli


@cli.command(name='supply-chain', short_help="Supply chain search utility")
@click.option('--app-name', help='The app name to find the supply chain for (domain or name)')
@click.pass_obj
def supply_chain(nudge_client: NudgeClient, app_name):
    app_resolution = utility.resolve_app(app_name=app_name, nudge_client=nudge_client, interactive=True)
    if app_resolution.status == ResolutionStatus.RESOLVED:
        suppliers = nudge_client.get_supply_chain(utility.get_canonical_domain(app_resolution.app))
        click.secho(f"{app_resolution.print_app_name()}")
        for supplier in suppliers:
            click.secho(f"\t{supplier['app_name']} - {supplier['domain_canonical']}")
