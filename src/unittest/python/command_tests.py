import os
import unittest

from click.testing import CliRunner

from nudge_bot.main import cli

DIRNAME = os.path.dirname(os.path.abspath(__file__))


def _get_absolute_path_for_resource(file):
    return os.path.abspath(os.path.join(DIRNAME, f"../resources/{file}"))


class CommandlineTestCase(unittest.TestCase):

    def test_list_fields(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['list-fields'])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout}")

    def test_set_fields(self):
        runner = CliRunner()
        result = runner.invoke(cli,
                               ['set-app-field', '--field', "APPROVAL STATUS", "--value", "ACCEPTABLE", "--app-name",
                                "zoom"], input="y\n")
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_search_app(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['search-app', '--app-name', "zoom"])
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")
    def test_search_app_field(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['search-app',"--field-name", "Approval Status", "--field-value", "Approved",
                                     "--field-name", "Approval Status", "--field-value", "Acceptable"
                                     ])
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_bulk_app_set(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['bulk-set-app-field', '--field', "APPROVAL STATUS", "--value", "ACCEPTABLE",
                                         '--app-list', _get_absolute_path_for_resource("transformed_list.txt")])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_bulk_app_value_set(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['bulk-set-app-field', '--field', "Approval Status", '--dry-run',
                                         '--app-value-list', _get_absolute_path_for_resource("transformed_list.txt")])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_create_duplicate_field(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['create-field', '--field-name', "Legal Review", "--field-type", "Select",
                                     '--field-scope', 'app', '--allowed-value', "In Review", '--allowed-value',
                                     "Approved"])
        print(result.stdout)
        self.assertEqual(result.exit_code, 1, f"Did not get good exit code: {result.stdout} {result.exception}")

    # def test_create_field(self):
    #     runner = CliRunner()
    #     result = runner.invoke(cli, ['create-field', '--field-name', "Legal Review", "--field-type", "Select",
    #                                  '--field-scope', 'SAAS', '--allowed-value', "In Review", '--allowed-value',
    #                                  "Approved"])
    #     print(result.stdout)
    #     self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")
    # def test_add_okta_support(self):
    #     runner = CliRunner()
    #     result = runner.invoke(cli, ['set-okta-support-field', '--okta-dict', "/Users/rspitler/code/nudge-frontend/service/src/main/python/service_rest_api/api/okta_dict.json"])
    #     print(result.stdout)
    #     self.assertEqual(result.exit_code, 1, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_update_field(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['update-field', '--field-identifier', "9256",
                                     '--field-name', "Legal Review",'--field-scope', 'app', '--allowed-value',
                                     "In Review", '--allowed-value', "Approved", "--allowed-value","Out of Scope"])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_transform_app_list(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['transform-app-list', '--app-list',
                                         _get_absolute_path_for_resource("app_list.txt")])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_supply_chain_list(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['supply-chain', '--app-name',
                                         'teams'])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_service_info(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['app-info', '--domain',
                                         'slack.com'])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_transform_app_value_list(self):
        runner = CliRunner(mix_stderr=True)
        result = runner.invoke(cli, ['transform-app-list', '--app-list',
                                         _get_absolute_path_for_resource("app_value_list.txt")])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_transform_ambig_app_list(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['transform-app-list', '--app-list',
                                     _get_absolute_path_for_resource("ambiguous_app_name.txt")], input="1\n")
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_search_app_by_field_list(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['search-app', '--field-name',"Approval Status", "--field-value","Approved", "--output-to-file"])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_search_app_by_field_not_set(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['search-app', '--field-name',"Approval Status", "--field-value","None", "--output-to-file"])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")
    def test_search_app_by_category(self):
            runner = CliRunner()
            with runner.isolated_filesystem():
                result = runner.invoke(cli, ['search-app', '--category',"AI Tools",  "--output-to-file"])
            print(result.stdout)
            self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_search_app_by_multiple_field_list(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['search-app',
                                         '--field-name', "Approval Status", "--field-value","Approved",
                                         '--field-name', "SSO Provider", "--field-value","Okta",
                                         "--output-to-file","--output-format","CSV"])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")
