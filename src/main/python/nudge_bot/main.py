import click

from nudge_bot.api.nudge import NudgeClient



@click.group()
@click.option('--refresh-token', envvar='REFRESH_TOKEN',  help='Bearer token for authentication')
@click.pass_context
def cli(ctx, refresh_token):
    ctx.obj = NudgeClient(refresh_token)


# noinspection PyUnresolvedReferences
from nudge_bot.commands import list, set_app_field, search_app, bulk_set_app_fields,\
    create_field, transform_app_list, update_field, set_okta_support