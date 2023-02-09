import logging
import uuid

import requests
from click import ClickException

from nudge_bot.api.congito_helper import Cognito

nudge_url_target = "https://www.nudgesecurity.io"


class NudgeClient:

    def __init__(self, refresh_token) -> None:
        super().__init__()
        self.fields = None
        self.cognito_config = self.get("/api/config/auth", auth=False)['config']
        self.cognito = Cognito(user_pool_id=self.cognito_config['aws_user_pools_id'],
                               user_pool_region=self.cognito_config['aws_project_region'],
                               client_id=self.cognito_config['aws_user_pools_web_client_id'],
                               refresh_token=refresh_token)
        self.cognito.renew_access_token()
        self.session = requests.session()

    def get_bearer_token(self):
        pass

    def get(self, url, auth=True):
        response = requests.get(f"{nudge_url_target}{url}", headers=self._get_auth_header() if auth else None)
        if response.status_code == 200:
            return response.json()
        else:
            logging.debug(response)
            raise Exception(f"Request failed {url} - {response.status_code}")

    def _get_auth_header(self, csrf=False):
        if not self.cognito.check_token():
            self.cognito.renew_access_token()
        bearer_token = self.cognito.access_token
        headers = {"authorization": f"Bearer {bearer_token}"}
        if csrf:
            token = self._get_csrf_token()
            if token:
                headers['x-csrftoken'] = token
        return headers

    def list_fields(self):
        if not self.fields:
            response_json = self.get(f"/api/fields/")
            self.fields = response_json['fields']
        return self.fields

    def get_ids_for_field_and_value(self, field: str, value):
        field_id = None
        value_id = None
        field_list = self.list_fields()
        for field_def in field_list:
            if field.lower() == field_def['name'].lower():
                field_id = field_def['id']
                for value_def in field_def['allowed_values']:
                    if value.lower() == value_def['value'].lower():
                        value_id = value_def['id']
        if not field_id or not value_id:
            raise ClickException(f"Can not locate field and value {field} - {value}")
        return field_id, value_id

    def _get_csrf_token(self):
        token = self._get_csrf_token_from_cookies()
        if not token:
            # run a get request in case this is our first call and there is no token
            self.session.get(f"{nudge_url_target}/api/fields/", headers=self._get_auth_header())
            token = self._get_csrf_token_from_cookies()
        return token

    def _get_csrf_token_from_cookies(self):
        return next((cookie.value for cookie in self.session.cookies if cookie.name == "_csrf_token"), None)

    def set_app_field(self, entity, field_id, value_id):
        body = {
            "value": str(value_id)
        }
        api = f"/api/fields/{field_id}/saas/{entity}"
        self.post(api, body)
        return True

    def post(self, api, body):
        response = self.session.post(f"{nudge_url_target}{api}", json=body,
                                     headers=self._get_auth_header(csrf=True))
        if response.status_code == 200:
            return response.json()
        else:
            raise ClickException(f"Error with post {api} {response.json()}")
    def put(self, api, body):
        response = self.session.put(f"{nudge_url_target}{api}", json=body,
                                     headers=self._get_auth_header(csrf=True))
        if response.status_code == 200:
            return response.json()
        else:
            raise ClickException(f"Error with put {api} {response.json()}")

    def find_app(self, app_name):
        # {"search":[{"field":"service_info.name","op":"ilike","value":"%Zoom%"},{"field":"service_info.category.name","op":"ilike","value":"%Zoom%"}],"filters":[],"page":1,"per_page":50,"sort":"account_count","sort_dir":"desc"}
        search = {"search": [{"field": "service_info.name", "op": "ilike", "value": f"%{app_name}%"},
                             {"field": "service_info.service_canonical_domain", "op": "ilike", "value": f"%{app_name}%"}],
                  "filters": [], "page": 1, "per_page": 50, "sort": "account_count", "sort_dir": "desc"}

        response = self.post("/api/analysis/app/search", search)
        return response['values']

    def find_field(self, field_name, field_id=None):
        fields = self.list_fields()
        for field_def in fields:
            if field_id and field_def['id'] == field_id:
                return field_def
            if field_def['name'] == field_name:
                return field_def
        return None

    def create_field(self, field_name, field_type, allowed_values, field_scope):
        body = {
            "name": field_name,
            "field_type": field_type.upper(),
            "scopes": [field_s.upper() for field_s in field_scope]
        }
        if allowed_values:
            body['allowed_values'] = [{'identifier': str(uuid.uuid4()), "value": value} for value in allowed_values]
        self.post('/api/fields/', body=body)

    def update_field(self, field_identifier, field_name, allowed_values, field_scope):
        body = {
            "identifier":field_identifier,
        }
        if field_name:
            body['name'] = field_name
        if field_scope and len(field_scope) >0:
            body['scopes'] = [field_s.upper() for field_s in field_scope]
        if allowed_values:
            body['allowed_values'] = [{'identifier': str(uuid.uuid4()), "value": value} for value in allowed_values]
        self.put('/api/fields/', body=body)
