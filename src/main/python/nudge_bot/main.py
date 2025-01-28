import click

from nudge_bot.api.nudge import NudgeClient



@click.group()
@click.option('--api-token', envvar='API_TOKEN',  help='Bearer token for authentication')
@click.pass_context
def cli(ctx, api_token):
    ctx.obj = NudgeClient(api_token)


# noinspection PyUnresolvedReferences
from nudge_bot.commands import list, set_app_field, search_app, bulk_set_app_fields,\
    create_field, transform_app_list, update_field, set_okta_support, supply_chain, service_info