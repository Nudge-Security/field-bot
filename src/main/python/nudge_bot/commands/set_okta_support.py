import json

import click
from click import ClickException, progressbar

from nudge_bot.api import nudge, utility
from nudge_bot.api.nudge import NudgeClient
from nudge_bot.main import cli


@cli.command(name='set-okta-support-field',short_help="Set a field for a given app")
@click.option('--okta-dict', help='Okta support dictionary', type=click.File('r'), required=True)
@click.option('--use-flag',     help='Use a flag instead of individual values', is_flag=True,default=False)
@click.pass_obj
def set_okta_support(nudge_client:NudgeClient, okta_dict, use_flag):
    loaded_dict = json.load(okta_dict)
    supported_protocols = ['SAML', 'SWA', 'API', 'Bookmark Sign On Mode', 'OIDC', 'Custom Sign On Mode']
    acceptable_protocols = []
    if use_flag:
        click.secho("Which Okta support protocols would you like to consider as acceptable support?")
        for protocol in supported_protocols:
            if click.confirm(protocol):
                acceptable_protocols.append(protocol)

    with progressbar(loaded_dict.items()) as items:
        for key, value in items:
            apps = nudge_client.find_app(key, exact=True)
            app_id = None
            if len(apps) == 0:
                continue
            elif len(apps) == 1:
                app = apps[0]
                # click.confirm(f"We found one app - is this right? {utility.print_app(app)}",abort=True )
                app_id = app['id']
            else:
                count = 0
                click.secho(f"Found multiple apps for {key}",fg='blue')
                for app in apps:
                    count +=1
                    click.secho(f"{count}. {utility.print_app(app)}",fg='green')
                count += 1
                click.secho(f"{count}. Skip",fg='blue')
                index = click.prompt("Please input the number of the app you wish to set the field on: ",
                                      type=click.IntRange(1, count))
                if index == count:
                    continue
                app_id = apps[index-1]['id']
            okta_features = value['okta_features']
            click.secho(f"\nSetting okta support for {key} {okta_features}")
            if not use_flag:
                for feature in okta_features:
                    if feature in supported_protocols:
                        field_id = nudge_client.get_ids_for_field('OKTA Support', feature)
                        click.secho(f"\tSetting value {feature}")
                        nudge_client.set_app_field(app_id, field_id, value)
            else:
                if any(value in acceptable_protocols for value in okta_features):
                    field_id = nudge_client.get_ids_for_field('OKTA Support', 'Yes')
                    click.secho(f"\tSetting value 'Yes'")
                    nudge_client.set_app_field(app_id, field_id, 'Yes')


