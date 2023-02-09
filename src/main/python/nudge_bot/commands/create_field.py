import click
from click import ClickException

from nudge_bot.api import nudge
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli

@cli.command(name='create-field',short_help="Create a field")
@click.option('--field-name',     help='The field to create', required=True)
@click.option('--field-scope',     help='The scope for the field',type=click.Choice(['SAAS','SAAS_ACCOUNT','USER']), required=True)
@click.option('--field-type',     help='The type of field to create', type=click.Choice(['MultiSelect','Select']), default='Select', required=True)
@click.option('--allowed-value',     help='The value for the field (can be specified multpile times)', multiple=True)
@click.pass_obj
def create_field(nudge_client:NudgeClient,field_scope, field_name, field_type, allowed_value):
    if field_type.lower() in ['multiselect','select']:
        if not allowed_value or len(allowed_value)==0:
            raise ClickException(f"For field of type {field_type} you must specify at least one allowed value")
    existing_field = nudge_client.find_field(field_name)
    if existing_field is not None:
        raise ClickException(f"Field {field_name} already exists!")
    nudge_client.create_field(field_name, field_type, allowed_value, field_scope)
