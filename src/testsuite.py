import unittest
from unittest import TestSuite, TextTestRunner, TestLoader

from tests.util.factory import FactoryTest
from tests.core.filtermanager import FilterManagerTest
from tests.core.logmanager import LogManagerTest

loader = unittest.defaultTestLoader
suite = loader.loadTestsFromTestCase(FactoryTest)
suite.addTest(loader.loadTestsFromTestCase(FilterManagerTest))
suite.addTest(loader.loadTestsFromTestCase(LogManagerTest))

runner = TextTestRunner(verbosity=1)
runner.run(suite)

