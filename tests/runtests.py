#!/usr/bin/env python
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'colab.settings'
os.environ['COLAB_PLUGINS'] = 'tests/plugins.d'
os.environ['COLAB_SETTINGS'] = 'tests/colab_settings.py'
os.environ['COLAB_WIDGETS_SETTINGS'] = 'tests/widgets_settings.py'
os.environ['COLAB_WIDGETS'] = 'tests/widgets.d'
os.environ['COVERAGE_PROCESS_START'] = '.coveragerc'

import coverage

# Needs to come before the settings import, because some settings instantiate
# objetcs. If they are executed before the coverage startup, those lines
# won't be covered.
if os.path.exists('.coverage'):
    os.remove('.coverage')
coverage.process_startup()

import django
from django.conf import settings
from django.test.utils import get_runner


def run():
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    run()
