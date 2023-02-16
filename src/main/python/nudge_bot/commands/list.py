import click

from nudge_bot.api import nudge
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli

@cli.command(name='list-fields',short_help="List all of the fields for your organization")
@click.option('--field-name',     help='The field name to search (optional)', multiple=True)
@click.pass_obj
def list_fields(ctx:NudgeClient, field_name):
    field_list = ctx.list_fields()
    field_name = [field.lower() for field in field_name]
    for field in field_list:
        scopes = [scope['scope'] for scope in field['field_scopes']]
        if len(field_name) == 0 or field['name'].lower() in field_name:
            click.secho(f"Name: {field['name']} Identifier: {field['identifier']} Scope: {', '.join(scopes)}" , fg='green')
            for value in field['allowed_values']:
                click.secho(f"\tValue: {value['value']}", fg='blue')
