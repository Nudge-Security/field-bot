

import click
from click import ClickException

from nudge_bot.api import nudge, utility
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli


def _is_app_names(lines):
    for line in lines:
        if not line.isdigit():
            return True
    return False


@cli.command(name='bulk-set-app-field',short_help="Set a field for list of apps")
@click.option('--field',     help='The field to set', required=True)
@click.option('--value',     help='The value to set', required=True)
@click.option('--dry-run',     help='Just print the apps to be updated' , is_flag=True)
@click.option('--app-list',     help='A line delimited list of apps ids to set the field', type=click.File('r'), required=True)
@click.pass_obj
def list_fields(nudge_client:NudgeClient, field, value, app_list, dry_run):
    # do this to verify we can find the right field and value
    field_id, value_id = nudge_client.get_ids_for_field_and_value(field, value)
    lines = []
    for line in app_list.readlines():
        lines.append(line.strip())
    if _is_app_names(lines):
        raise ClickException("The app list appears to be names instead of app"
                             " ids use the 'transform-app-list' command to fix")

    for id in lines.items():
        if dry_run:
            click.secho(f"Updating: {id}")
        else:
            click.secho(f"Updating : {id} to {field} : {value}")
            nudge_client.set_app_field(id, field_id, value_id)
    click.secho(f"Finished updating {len(lines)}")
