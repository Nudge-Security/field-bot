#   -*- coding: utf-8 -*-
import os

from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.flake8")
# use_plugin("python.coverage")
use_plugin("python.distutils")


name = "nudge-bot"
default_task = "publish"


@init
def set_properties(project):
    project.author = "Nudge Security"
    project.depends_on_requirements("src/main/python/requirements.txt")
    # project.build_depends_on_requirements("src/main/python/requirements.txt")
    project.summary = "CLI access to update Nudge Security"
    project.name = "nudge-bot"
    project.license = "Apache 2.0"
    project.home_page = f"https://github.com/Nudge-Security/nudge-bot"
    project.set_property_if_unset("coverage_break_build", False)
    project.url = f"https://github.com/Nudge-Security/nudge-bot"
    project.description = "CLI to update, search and access nudgesecurity.io"
    project.set_property("distutils_upload_repository", "pypi")
    # Configure build number for running in bitbucket
    project.set_property_if_unset("build_number", os.environ.get("GITHUB_RUN_NUMBER", None))
    project.set_property_if_unset("dir_target","target")
    project.set_property("dir_reports", os.path.join(project.get_property("dir_target"), "test-reports"))
    build_number = project.get_property("build_number")
    if build_number is not None and "" != build_number:
        project.version = f"0.1.{build_number}"
    else:
        project.version = "0.0.999"
