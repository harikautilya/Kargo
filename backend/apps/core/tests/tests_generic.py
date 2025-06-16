from django.test import TestCase

# Create your tests here.
class SampleTestCase(TestCase):

  def setUp(self):
    pass
  def test_check(self):
    self.assertEqual(2, 1+1)
