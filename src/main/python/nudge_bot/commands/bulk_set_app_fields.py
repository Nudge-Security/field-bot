

import click
from click import ClickException, progressbar

from nudge_bot.api import nudge, utility
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli


def _is_app_names(lines):
    for line in lines:
        if not line[0].isdigit():
            return True
    return False


@cli.command(name='bulk-set-app-field',short_help="Set a field for list of apps")
@click.option('--field',     help='The field to set', required=True)
@click.option('--value',     help='The value to set ')
@click.option('--dry-run',     help='Just print the apps to be updated' , is_flag=True)
@click.option('--app-list',     help='A line delimited list of apps ids to set the field', type=click.File('r'))
@click.option('--app-value-list',     help='A line delimited list of apps ids and values to set the field', type=click.File('r'))
@click.pass_obj
def list_fields(nudge_client:NudgeClient, field, value, app_list,app_value_list, dry_run):
    if app_list and app_value_list:
        raise ClickException("Only one of --app-list or --app-value-list may be provided")
    if not app_list and not app_value_list:
        raise ClickException("At least one of --app-list or --app-value-list must be provided")
    if app_list and not value:
        raise ClickException("When using --app-list a --value must be provided")
    dynamic_values = app_value_list is not None
    to_read = app_list if app_list else app_value_list

    # do this to verify we can find the right field and value
    field_id, value_id = nudge_client.get_ids_for_field_and_value(field, value)
    lines = []
    for line in to_read.readlines():
        lines.append(line.strip().split(','))
    if _is_app_names(lines):
        raise ClickException("The app list appears to be names instead of app"
                             " ids use the 'transform-app-list' command to fix")

    with progressbar(lines) as apps:
        for meta in apps:
            if len(meta) > 3:
                raise ClickException(f"Entry found with too many values {meta}")
            id = meta[0]
            name = meta[1]
            if dynamic_values:
                if len(meta) != 3:
                    raise ClickException(f"Entry found without all values {meta}")
                value = meta[2].strip()
                field_id, value_id = nudge_client.get_ids_for_field_and_value(field, value)

            if dry_run:
                click.secho(f"Updating: {name}  to {field} : {value}")
            else:
                nudge_client.set_app_field(id, field_id, value_id)
    click.secho(f"Finished updating {len(lines)}")
