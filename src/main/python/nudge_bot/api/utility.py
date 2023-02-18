import enum
from collections import defaultdict
from typing import List

import click
import pydash

from nudge_bot.api.nudge import NudgeClient


def print_app(app):
    return f"{get_app_name(app)}: {app['account_count']}"


def get_app_name(app):
    name_ = app['service_info']['name'] if app['service_info']['name'] else app['name']
    return name_.replace(',', '')


class ResolutionStatus(enum.Enum):
    RESOLVED = "RESOLVED",
    AMBIGUOUS = "AMBIGUOUS",
    NOT_FOUND = "NOT_FOUND"


class AppResolution:

    def __init__(self, status: ResolutionStatus, app_name, ambiguous_count=None, app=None) -> None:
        super().__init__()
        self.app = app
        self.ambiguous_count = ambiguous_count
        self.status = status
        self.app_name = app_name
        self.value = None

    def add_meta_data(self, value):
        self.value = value

    def print(self):
        match self.status:
            case ResolutionStatus.AMBIGUOUS:
                return f"{self.print_app_name()}: {self.ambiguous_count}"
            case ResolutionStatus.NOT_FOUND:
                return f"{self.print_app_name()}"
            case _:
                base = f"{self.app['id']}, {self.print_app_name()}"
                if self.value: return f"{base}, {self.value}"
                return base

    def print_app_name(self):
        if self.app:
            return get_app_name(self.app)
        else:
            return self.app_name


class AppResolutionCollection:

    def __init__(self) -> None:
        super().__init__()
        self.resolutions = defaultdict(list)

    def add(self, app_resolution: AppResolution):
        self.resolutions[app_resolution.status].append(app_resolution)

    def get(self, status: ResolutionStatus) -> List[AppResolution]:
        return self.resolutions[status]

    def count(self, status: ResolutionStatus) -> int:
        return len(self.get(status))


def resolve_app(app_name, nudge_client: NudgeClient, interactive=False) -> AppResolution:
    apps = nudge_client.find_app(app_name=app_name)
    if not apps or len(apps) == 0:
        if interactive:
            if click.confirm(f"\nUnable to find app {app_name}, would you like to enter a new search?"):
                new_search = click.prompt(f"Please enter new search for {app_name}", type=str)
                return resolve_app(new_search, nudge_client, interactive=interactive)
            else:
                return AppResolution(ResolutionStatus.NOT_FOUND, app_name)
        else:
            return AppResolution(ResolutionStatus.NOT_FOUND, app_name)
    if len(apps) > 1:
        if not interactive:
            return AppResolution(ResolutionStatus.AMBIGUOUS, app_name, len(apps))
        click.secho(f"Found ambiguous app name {app_name}", fg='red')
        count = 0
        for app in apps:
            count += 1
            click.secho(f"{count}. {print_app(app)}", fg='green')
        count += 1
        search_again = count
        click.secho(f"{count}. Re-enter search term", fg='blue')
        count += 1
        skip = count
        click.secho(f"{count}. Skip", fg='blue')
        option = click.prompt("Please input the number of the app you wish to select", type=click.IntRange(1, count))
        if option == search_again:
            new_search = click.prompt(f"Please enter new search for {app_name}", type=str)
            return resolve_app(new_search, nudge_client, interactive=interactive)
        if option == skip:
            return AppResolution(ResolutionStatus.AMBIGUOUS, app_name, len(apps))
        app = apps[option - 1]
    else:
        app = apps[0]
    return AppResolution(status=ResolutionStatus.RESOLVED, app_name=app_name, app=app)


def _get_field_value(name, fields_):
    found_fields = pydash.filter_(fields_, lambda x: pydash.get(x, 'field.name') == name)
    if len(found_fields)>0:
        return ":".join(pydash.flat_map(found_fields,lambda x: pydash.get(x,'allowed_value.value')))
    return 'Not Set'


def get_fields(value, field_names):
    fields_ = value['fields']
    ret = []
    for name in field_names:
        ret.append(_get_field_value(name,fields_))
    return ret


def get_category(app):
    return pydash.get(app,'service_info.category.name')


def get_account_count(app):
    return pydash.get(app,'counters.total_accounts')


def _extract_scopes(x):
    return pydash.flat_map(pydash.get(x,'field_scopes') ,lambda y: y['scope'])


def get_field_names(fields, scope=None):
    fields = sorted(fields,key=lambda field: field['name'])
    if scope:
        fields = pydash.filter_(fields, lambda x: (scope.lower() in _extract_scopes(x)))
    return [ field['name'] for field in fields]