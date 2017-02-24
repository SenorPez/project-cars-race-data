from unittest import TestCase

from racedata.Driver import Driver


class TestDriver(TestCase):
    def test_get_initial(self):
        instance = Driver("Kobernulf Monnur")
        self.assertEqual(instance.get_initial(), "K")

