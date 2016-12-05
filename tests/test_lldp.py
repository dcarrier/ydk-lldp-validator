import unittest
import lldp
import yaml
import os
from mock import MagicMock

class GeneralLLDPTestCase(unittest.TestCase, object):

	def test_format_interface_good_data(self):
		location = os.path.dirname(os.path.realpath(__file__))
		new_filepath = os.path.join(location, "tests/_formatInterface/fI_Data.yaml")
		with open(new_filepath) as f: 
			dataMap = yaml.safe_load(f)
		goodData = []
		for i in dataMap["Good_Data"]:
			print i
			x = lldp._formatInterface(i)
			print x
			goodData.append(x[-1])
		self.assertEqual(goodData, dataMap["Good_Formated"])

	def test_format_interface_bad_data(self):
		location = os.path.dirname(os.path.realpath(__file__))
		new_filepath = os.path.join(location, "tests/_formatInterface/fI_Data.yaml")
		with open(new_filepath) as f: 
			dataMap = yaml.safe_load(f)
		f.close()
		badData = []
		with self.assertRaises(SystemExit):
			for i in dataMap["Bad_Data"]:
				print i
				x = lldp._formatInterface(i)
				print x5
				badData.append(x[-1])

	def test_format_interface_no_data(self):
		print ""

	def test_get_host(self):
		lldp.crud = MagicMock()
		lldp.crud.read = MagicMock()
		lldp.provoider = MagicMock()
		import pdb
		pdb.set_trace()
		lldp._getHost(lldp.crud, lldp.provider)
		lldp.crud.read.assert_called_with(lldp.provider, lldp._getHost.shell_util)

