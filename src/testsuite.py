import unittest
from unittest import TestSuite, TextTestRunner, TestLoader

from tests.util.factory import FactoryTest
from tests.core.filtermanager import FilterManagerTest
from tests.core.logmanager import LogManagerTest
from tests.core.controller import ControllerTest
from tests.filter.ipfilter import IPFilterTest
from tests.filter.portfilter import TCPFilterTest, UDPFilterTest
from tests.logger.pcaplogger import PcapLoggerTest
from tests.logger.textlogger import TextLoggerTest

loader = unittest.defaultTestLoader
suite = loader.loadTestsFromTestCase(FactoryTest)
suite.addTest(loader.loadTestsFromTestCase(FilterManagerTest))
suite.addTest(loader.loadTestsFromTestCase(LogManagerTest))
suite.addTest(loader.loadTestsFromTestCase(ControllerTest))
suite.addTest(loader.loadTestsFromTestCase(IPFilterTest))
suite.addTest(loader.loadTestsFromTestCase(TCPFilterTest))
suite.addTest(loader.loadTestsFromTestCase(UDPFilterTest))
suite.addTest(loader.loadTestsFromTestCase(PcapLoggerTest))
suite.addTest(loader.loadTestsFromTestCase(TextLoggerTest))

runner = TextTestRunner(verbosity=1)
runner.run(suite)

