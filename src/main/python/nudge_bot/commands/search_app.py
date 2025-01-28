import click
from click import ClickException

from nudge_bot.api import nudge, utility
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli


@cli.command(name='search-app', short_help="Search for an app")
@click.option('--app-name', help='The app name')
@click.option('--category', help='The app category')
@click.option('--field-name', help='The field name to search (optional)', multiple=True)
@click.option('--field-value', help="The field value to search (use \'None\' to search for unset fields)",
              multiple=True)
@click.option('--output-to-file', help='Use this flag print to file', is_flag=True)
@click.option('--output-format', help='The output format', type=click.Choice(['Id', 'CSV']), default='CSV')
@click.option('--output-file', help='The file to write the search results', type=click.File('w'),
              default="search_list.csv")
@click.pass_obj
def search_app(nudge_client: NudgeClient, app_name,category, field_name, field_value, output_to_file, output_file,
                output_format):
    if len(field_name) != len(field_value):
        raise ClickException("Please provide values for every field to search, use \'None\' to search for unset fields")
    if app_name:
        values = nudge_client.find_app(app_name)
    elif category:
        values = nudge_client.find_app_by_category(category)
    elif len(field_name) > 0:
        values = nudge_client.find_app_by_field(field_name, field_value)
    else:
        raise ClickException("Must provide either --app-name or --field-name")
    if len(values) == 0:
        if app_name:
            click.secho(f"No apps found for name: {app_name}", fg='red')
        else:
            click.secho(f"No apps found for field: {field_name} value: {values}", fg='red')
    else:
        fields = nudge_client.list_fields()
        field_names = utility.get_field_names(fields, 'SaaS')
        if output_to_file:
            if output_format == 'CSV':
                output_file.writelines(f"App, Category, Accounts,{','.join(field_names)}\n")

        for value in values:
            click.secho(utility.print_app(value))
            if output_to_file:
                if output_format == 'Id':
                    out = f"{value['id']}\n"
                else:
                    out = f"{utility.get_app_name(value)},{utility.get_category(value)},{utility.get_account_count(value)},{','.join(utility.get_fields(value, field_names))}\n"
                output_file.writelines(out)
