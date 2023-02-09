import click

from nudge_bot.api import nudge
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli

@cli.command(name='list-fields',short_help="List all of the fields for your organization")
@click.pass_obj
def list_fields(ctx:NudgeClient):
    field_list = ctx.list_fields()
    for field in field_list:
        click.secho(f"Name: {field['name']} Identifier: {field['identifier']} Scope: {field['field_scopes']}" , fg='green')
        for value in field['allowed_values']:
            click.secho(f"\tValue: {value['value']}", fg='blue')
