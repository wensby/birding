from unittest import TestCase
from unittest.mock import Mock
from birding.sighting import SightingRepository
from birding.sighting import Sighting
from datetime import datetime, date


class TestSighting(TestCase):

  def test_eq_false_when_other_type(self):
    sighting = Sighting(4, 8, 15, date(2019, 7, 12), None)
    self.assertNotEqual(sighting, 'Sighting(4, 8, 15, date(2019, 7, 12), None)')

  def test_repr(self):
    sighting = Sighting(4, 8, 15, date(2019, 7, 12), None)
    self.assertEqual(repr(sighting), 'Sighting(4, 8, 15, 2019-07-12, None)')

class TestSightingRepository(TestCase):

  def setUp(self):
    self.database = Mock()
    self.repository = SightingRepository(self.database)

  def test_find_sighting_returns_sighting_when_present(self):
    now = datetime.now()
    date = now.date()
    time = now.time()
    self.database.query().rows = [[4, 8, 15, date, time]]
    sighting = self.repository.find_sighting(1337)
    self.assertEqual(sighting, Sighting(4, 8, 15, date, time))

  def test_find_sighting_returns_none_when_not_present(self):
    self.database.query().rows = []
    sighting = self.repository.find_sighting(1337)
    self.assertIsNone(sighting)

  def test_find_sighting_queries_database_correctly(self):
    self.database.query().rows = []
    self.repository.find_sighting(1337)
    self.database.query.assert_called_with(
      'SELECT id, person_id, bird_id, sighting_date, sighting_time '
      'FROM sighting WHERE id = %s;', (1337,))

  def test_delete_sighting_queries_database_correctly(self):
    self.database.query().status = 'DELETE 1'
    self.repository.delete_sighting(1337)
    self.database.query.assert_called_with(
      'DELETE FROM sighting WHERE id = %s;', (1337,))