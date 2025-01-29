import logging

import requests
from click import ClickException
from tldextract import tldextract

nudge_url_target = "https://api.nudgesecurity.io/api/1.0"


def _transform_app_name(app_name):
    is_domain = _is_domain(app_name)
    if is_domain:
        loc = tldextract.extract(app_name)
        return str(loc.domain)
    return app_name


def _is_domain(app_name):
    return 'http' in app_name


class NudgeClient:

    def __init__(self, api_token) -> None:
        super().__init__()
        self.fields = None
        self.access_token = api_token
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

    def post(self, api, body):
        response = self.session.post(f"{nudge_url_target}{api}", json=body,
                                     headers=self._get_auth_header())
        if response.status_code == 200:
            return response.json()

        else:
            raise ClickException(f"Error with post {api} {response.json()}")

    def put(self, api, body):
        response = self.session.put(f"{nudge_url_target}{api}", json=body,
                                    headers=self._get_auth_header())
        if response.status_code == 200:
            return response.json()
        else:
            raise ClickException(f"Error with put {api} {response.json()}")

    def _get_auth_header(self):
        bearer_token = self.access_token
        headers = {"authorization": f"Bearer {bearer_token}"}
        return headers

    def list_fields(self):
        if not self.fields:
            search = {"search": [],
                      "filters": [], "page": 1, "per_page": 50}

            response_json = self.post(f"/fields/search", search)
            self.fields = response_json['values']
        return self.fields

    def get_ids_for_field(self, field: str, value=None):
        field_id = None
        value_id = None
        field_list = self.list_fields()
        for field_def in field_list:
            if field.lower() == field_def['name'].lower():
                field_id = field_def['id']
        if not field_id:
            raise ClickException(f"Can not locate field and value {field}")
        return field_id


    def value_exists(self, field_identifier, value:str):
        field_list = self.list_fields()
        for field in field_list:
            if str(field['id']) == field_identifier:
                for exist_value in field['allowed_values']:
                    if exist_value['value'].lower() == value.lower():
                        return True
        return False

    def set_app_field(self, app_id, field_id, value_id):
        body = {
            "value": str(value_id)
        }
        api = f"/apps/{app_id}/fields/{field_id}"
        self.post(api, body)
        return True

    def find_app_by_field(self, field_name=None, field_value=None, page=None):
        search = {"search": [],
                  "filters": [], "page": 1 if not page else page, "per_page": 100,
                  "sorting": {"property": "account_count", "direction": "desc"}}
        for field, value in zip(field_name, field_value):
            if value == 'None':
                search['search'].append({"property": "fields", "op": "isnull", "field_name": field, "value": value})
            else:
                search['search'].append({"property": "fields", "op": "=", "field_name": field, "value": value})
        response = self.post("/apps/search", search)
        ret = response['values']
        if response['next_page']:
            ret.extend(self.find_app_by_field(field_name, field_value, response['next_page']))
        return ret

    def find_app_by_category(self, category):
        search = {"search": [{"property": "category", "op": "=", "value": category}],
                  "filters": [],
                  "sorting": {"property": "account_count", "direction": "desc"}}
        return self._find_app(search=search)
    def find_app(self, app_name, page=None, exact=False):
        is_domain = _is_domain(app_name)
        app_name = _transform_app_name(app_name)
        # {"search":[{"field":"service_info.name","op":"ilike","value":"%Zoom%"},{"field":"service_info.category.name","op":"ilike","value":"%Zoom%"}],"filters":[],"page":1,"per_page":50,"sort":"account_count","sort_dir":"desc"}
        if exact:
            op = "="
            val = f"{app_name}"
        else:
            op = "ilike"
            val = f"%{app_name}%"
        search = {"search": [],
                  "filters": [],
                  "sorting": {"property": "account_count", "direction": "desc"}}
        if is_domain:
            search['search'].append({"property": "domain_canonical", "op": op, "value": val})
        else:
            search['search'].append({"property": "service_info.name", "op": op, "value": val})
            search['search'].append({"property": "name", "op": op, "value": val})

        return self._find_app(search)

    def _find_app(self, search, page=None):
        search["page"] = 1 if not page else page
        search["per_page"] = 50
        response = self.post("/apps/search", search)
        ret = response['values']
        if response['next_page']:
            ret.extend(self._find_app(search=search, page=response['next_page']))
        return ret

    def find_field(self, field_name, field_identifier=None):
        fields = self.list_fields()
        for field_def in fields:
            if field_identifier and str(field_def['id']) == field_identifier:
                return field_def
            if field_def['name'] == field_name:
                return field_def
        return None

    def create_field(self, field_name, field_type, allowed_values, field_scope):
        body = {
            "name": field_name,
            "field_type": field_type.upper(),
            "scopes": [field_s.lower() for field_s in field_scope]
        }
        response = self.post('/fields', body=body)
        field_id = response['id']
        for value in allowed_values:
            self.update_field(field_identifier=field_id, allowed_values=value)

    def update_field(self, field_identifier, field_name=None, allowed_values=None, field_scope=None):
        body = {}
        if field_name:
            body['name'] = field_name
        if field_scope and len(field_scope) > 0:
            body['scopes'] = [field_s.lower() for field_s in field_scope]
        self.put(f'/fields/{field_identifier}', body=body)
        if allowed_values:
            for value in allowed_values:
                if not self.value_exists(field_identifier, value):
                    self.post(f'/fields/{field_identifier}/allowed_values', body={
                        "value": value
                    })

    def get_supply_chain(self, canonical_domain):
        return self.get(f'/api/service/vendors/{canonical_domain}')['vendors']

    def get_service_info(self, canonical_domain):
        return self.get(f'/api/service/details/{canonical_domain}')

