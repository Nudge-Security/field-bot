
import click
from click import ClickException

from nudge_bot.api import nudge, utility
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli


@cli.command(name='search-app',short_help="Search for an app")
@click.option('--app-name',     help='The app name')
@click.option('--field-name',     help='The field name to search (optional)', multiple=True)
@click.option('--field-value',     help="The field value to search (use \'None\' to search for unset fields)", multiple=True)
@click.option('--output-id-list',     help='Use this flag print a list of app ids to file', is_flag=True)
@click.option('--output-file',     help='The file to write the search results', type=click.File('w'), default="search_list.txt")
@click.pass_obj
def list_fields(nudge_client:NudgeClient, app_name, field_name, field_value,output_id_list, output_file):
    if len(field_name) != len(field_value):
        raise ClickException("Please provide values for every field to search, use \'None\' to search for unset fields")
    if app_name:
        values = nudge_client.find_app(app_name)
    elif len(field_name)>0:
        values = nudge_client.find_app_by_field(field_name,field_value)
    else:
        raise ClickException("Must provide either --app-name or --field-name")
    if len(values) == 0:
        if app_name:
            click.secho(f"No apps found for name: {app_name}",fg='red' )
        else:
            click.secho(f"No apps found for field: {field_name} value: {values}",fg='red' )
    else:
        for value in values:
            click.secho(utility.print_app(value))
            if output_id_list:
                output_file.writelines(f"{value['id']}\n")


