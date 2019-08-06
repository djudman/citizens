#!/usr/bin/env python3
import importlib.util
import os
from os.path import dirname
import sys
import time
import unittest


def import_module_by_path(path):
    spec = importlib.util.spec_from_file_location('test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_test_modules():
    test_modules = []
    current_dir = os.path.dirname(os.path.realpath(__file__))
    for dirpath, _, filenames in os.walk(current_dir):
        for name in filenames:
            if name.startswith('test') and name.endswith('.py'):
                path = os.path.join(dirpath, name)
                module = import_module_by_path(path)
                test_modules.append(module)
    return test_modules


if __name__ == '__main__':
    project_dir = dirname(dirname(os.path.realpath(__file__)))
    sys.path.append(project_dir)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for module in get_test_modules():
        suite.addTests(loader.loadTestsFromModule(module))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.failures:
        sys.exit(1)
