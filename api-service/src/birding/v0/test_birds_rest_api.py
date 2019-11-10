from http import HTTPStatus
from unittest import TestCase
from unittest.mock import Mock

from birding import LinkFactory, BirdRepository
from test_util import AppTestCase
from v0 import BirdsRestApi


class TestBird(AppTestCase):

  def setUp(self):
    super().setUp()
    self.db_insert_bird(1, 'Pica pica')

  def test_get_bird(self):
    self.db_insert_picture(1, 'image/bird/pica-pica-thumb.jpg', 'myCredit')
    self.db_insert_bird_thumbnail(1, 1)

    response = self.client.get('/birds/pica-pica')

    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertDictEqual(response.json, {
      'id': 'pica-pica',
      'binomialName': 'Pica pica',
      'thumbnail': {
        'url': 'myExternalHost/static/image/bird/pica-pica-thumb.jpg',
        'credit': 'myCredit',
      },
      'cover': {
        'url': 'myExternalHost/static/image/bird/pica-pica-thumb.jpg',
        'credit': 'myCredit',
      },
    })
    self.assert_rate_limit_headers(response, 59)

  def test_get_bird_with_minimal_data(self):
    response = self.client.get('/birds/pica-pica')

    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertDictEqual(response.json, {
      'id': 'pica-pica',
      'binomialName': 'Pica pica',
    })
    self.assert_rate_limit_headers(response, 59)

  def test_get_bird_rate_limited(self):
    response = None

    for _ in range(61):
      response = self.client.get('/birds/pica-pica')

    self.assertEqual(response.status_code, HTTPStatus.TOO_MANY_REQUESTS)
    self.assertDictEqual(response.json, {
      'error': 'rate limit exceeded 60 per 1 minute'
    })
    self.assert_rate_limit_headers(response, 0)

  def test_get_bird_when_not_found(self):
    response = self.client.get('/birds/content-not-found')

    self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    self.assertDictEqual(response.json, {
      'message': 'Not Found'
    })

  def assert_rate_limit_headers(self, response, expected_remaining):
    headers = response.headers
    self.assertIn('X-Rate-Limit-Limit', headers)
    self.assertIn('X-Rate-Limit-Remaining', headers)
    self.assertIn('X-Rate-Limit-Reset', headers)
    self.assertNotIn('Retry-After', headers)
    self.assertNotIn('X-RateLimit-Reset', headers)
    reset = int(headers['X-Rate-Limit-Reset'])
    limit = int(headers['X-Rate-Limit-Limit'])
    remaining = int(headers['X-Rate-Limit-Remaining'])
    self.assertLessEqual(reset, self.test_rate_limit_per_minute)
    self.assertEqual(limit, self.test_rate_limit_per_minute)
    self.assertEqual(remaining, expected_remaining)


class TestBirdsRestApi(TestCase):

  def test_get_bird_with_unexpected_bird_identifier_format(self):
    link_factory = Mock(spec=LinkFactory)
    bird_repository = Mock(spec=BirdRepository)
    api = BirdsRestApi(link_factory, bird_repository)

    with self.assertRaises(Exception):
      api.get_bird(1)