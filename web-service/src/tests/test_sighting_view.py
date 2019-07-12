from unittest import TestCase
from unittest.mock import Mock, ANY

from birding.sighting_view import SightingViewFactory
from birding.sighting_view import SightingItem
from birding.sighting_view import SightingCreationView
from birding.database import read_script_file
from tests.test_util import mock_return
from types import SimpleNamespace as Simple
from datetime import datetime


class TestSightingViewFactory(TestCase):

  def setUp(self):
    self.bird_repository = Mock()
    self.database = Mock()
    self.factory = SightingViewFactory(self.bird_repository, self.database)

  def test_create_sighting_items_returns_empty_list_when_no_sightings(self):
    self.database.query().rows = []
    result = self.factory.create_sighting_items(account=Simple(person_id=4))
    self.assertListEqual(result, [])

  def test_create_sighting_items_returns_correct_sighting_item(self):
    now = datetime.now()
    self.database.query().rows = [
      [4, 8, 'Pica pica', now.date(), now.time(), 'myPictureUrl1'],
      [15, 16, 'Ardea cinerea', now.date(), now.time(), 'myPictureUrl2'],
    ]

    result = self.factory.create_sighting_items(account=Simple(person_id=23))

    time = f'{now.date().isoformat()} {now.time().isoformat()}'
    expected_items = [
      SightingItem(4, 8, 'Pica pica', time, 'myPictureUrl1'),
      SightingItem(15, 16, 'Ardea cinerea', time, 'myPictureUrl2'),
    ]
    self.assertListEqual(result, expected_items)

  def test_create_sighting_items_queries_database_correctly(self):
    self.database.query().rows = []
    self.factory.create_sighting_items(account=Simple(person_id=4))
    self.database.query.assert_called_with(
      read_script_file('select_sighting_item_data.sql'), (4,))

  def test_create_sighting_creation_view_when_valid_bird_id(self):
    self.bird_repository.get_bird_by_id = mock_return('White wagtail')

    result = self.factory.create_sighting_creation_view(1)

    self.assertEqual(result, SightingCreationView('White wagtail'))
    self.bird_repository.get_bird_by_id.assert_called_with(1)
    self.bird_repository.get_bird_by_id.assert_called_once_with(ANY)
