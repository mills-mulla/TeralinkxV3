# apps/finance/tests.py
"""
Finance App Tests
Imports all test modules for discovery.
"""
from django.test import TestCase

# Import all test modules
from .tests.unit.test_models import *
from .tests.unit.test_services import *
from .tests.api.test_endpoints import *
from .tests.integration.test_workflows import *

# Test discovery will find all TestCase subclasses
