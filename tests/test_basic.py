import unittest


class BasicTest(unittest.TestCase):
	def setUp(self):
		print('Test is set up')

	def test_ok(self):
		self.assertTrue(True)


if __name__ == '__main__':
	unittest.main()
