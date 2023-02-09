import click
from click import ClickException

from nudge_bot.api import nudge
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli

@cli.command(name='update-field',short_help="Update a field")
@click.option('--field-id',     help='The field to update (use list-fields command)',type=int, required=True)
@click.option('--field-name',     help='An updated name for the field ', required=True)
@click.option('--field-scope',     help='Updated scopes for the field (must include existing scopes you wish to retain)',type=click.Choice(['SAAS','SAAS_ACCOUNT','USER']),multiple=True)
@click.option('--allowed-value',     help='Updated values for the field (multiple can be specified)', multiple=True)
@click.pass_obj
def list_fields(nudge_client:NudgeClient,field_scope, field_id:int, field_name, allowed_value):
    existing_field = nudge_client.find_field(field_id=field_id, field_name=None)
    if existing_field is None:
        raise ClickException(f"Field {field_id} can not be found!")
    nudge_client.update_field(field_id, field_name, allowed_value, field_scope)
