import os
import unittest
from multiprocessing.context import Process
from RQSSFramework.RQSS_Framework_Runner import write_results_to_CSV
#from src.RQSSFramework.RQSS_Framework_Runner import write_results_to_CSV

from RQSSFramework.Availability.DereferencePossibility import DerefOfURI



class TestFrameworkRunner(unittest.TestCase):
    def setUp(self):
        self.test_derefs=[DerefOfURI('http://seyedahbr.github.io',False),
        DerefOfURI('http://seyedahbr.github.io',False),
        DerefOfURI('http://seyedahbr.github.io',True),
        DerefOfURI('http://seyedahbr.github.io',False)]

    def test_write_results_to_CSV(self):
        write_results_to_CSV(self.test_derefs,'output.test.csv')
        self.assertTrue(os.path.exists('output.test.csv'))
        self.assertEqual(sum(1 for line in open('output.test.csv')),5)
