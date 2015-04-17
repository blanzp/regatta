__author__ = 'Paul'

from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("python.integrationtest")

name = "regatta"
default_task = ['run_unit_tests']


@init
def set_properties(project):
    project.build_depends_on('flake8')
    project.build_depends_on('boto')
    project.build_depends_on('flask')
    project.build_depends_on('pandas')
    project.build_depends_on('passlib')
    project.build_depends_on('simplejson')
    project.build_depends_on('wolfram')
    project.set_property('unittest_module_glob', 'test_*')
    project.set_property('integrationtest_module_glob', 'test_*')

