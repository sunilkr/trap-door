from unittest import TestSuite, TextTestRunner, TestLoader
from test.factory import FactoryTest

loader = TestLoader()
suite = loader.loadTestsFromTestCase(FactoryTest)

runner = TextTestRunner(verbosity=3)
runner.run(suite)

