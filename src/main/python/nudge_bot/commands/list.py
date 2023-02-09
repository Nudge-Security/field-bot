import click

from nudge_bot.api import nudge
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli

@cli.command(name='list',short_help="List all of the fields for your organization")
@click.pass_obj
def list_fields(ctx:NudgeClient):
    field_list = ctx.list_fields()
    for field in field_list:
        print(f"Name: {field['name']} Id: {field['id']}")
        for value in field['allowed_values']:
            print(f"\tValue: {value['value']} Id: {value['id']}")
