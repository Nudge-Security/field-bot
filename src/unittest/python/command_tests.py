import os
import unittest

from click.testing import CliRunner

from nudge_bot.main import cli

DIRNAME = os.path.dirname(os.path.abspath(__file__))


class CommandlineTestCase(unittest.TestCase):

    def _get_absolute_path_for_resource(self, file):
        return os.path.abspath(os.path.join(DIRNAME,f"../resources/{file}"))
    def test_list_fields(self):
        runner = CliRunner()
        result = runner.invoke(cli, [ 'list'])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout}")

    def test_set_fields(self):
        runner = CliRunner()
        result = runner.invoke(cli, [ 'set-app-field', '--field',"APPROVAL STATUS","--value", "ACCEPTABLE", "--app-name","zoom"], input="y\n")
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_search_app(self):
        runner = CliRunner()
        result = runner.invoke(cli, [ 'search-app', '--app-name',"zoom"])
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_bulk_app_set(self):
        runner = CliRunner()
        result = runner.invoke(cli, [ 'bulk-set-app-field', '--field',"APPROVAL STATUS","--value", "ACCEPTABLE", '--app-list',self._get_absolute_path_for_resource("app_list.txt")])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_bulk_app_ambiguous_app(self):
        runner = CliRunner()
        result = runner.invoke(cli, [ 'bulk-set-app-field', '--field',"APPROVAL STATUS","--value", "ACCEPTABLE",  '--app-list',self._get_absolute_path_for_resource("ambiguous_app_name.txt"), '--dry-run'])
        print(result.stdout)
        self.assertEqual(result.exit_code, 1, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_create_duplicate_field(self):
        runner = CliRunner()
        result = runner.invoke(cli, [ 'create-field', '--field-name',"Legal Review","--field-type", "Select",'--field-scope','SAAS', '--allowed-value',"In Review", '--allowed-value',"Approved"])
        print(result.stdout)
        self.assertEqual(result.exit_code, 1, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_transform_app_list(self):
        runner = CliRunner()
        result = runner.invoke(cli, [ 'transform-app-list', '--app-list',self._get_absolute_path_for_resource("app_list.txt")])
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")

    def test_transform_ambig_app_list(self):
        runner = CliRunner()
        result = runner.invoke(cli, [ 'transform-app-list', '--app-list',self._get_absolute_path_for_resource("ambiguous_app_name.txt")], input="1\n")
        print(result.stdout)
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout} {result.exception}")
