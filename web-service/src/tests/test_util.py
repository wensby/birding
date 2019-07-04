from http import HTTPStatus
from unittest import TestCase
from unittest.mock import Mock

from flask import url_for
from flask.testing import FlaskClient
from requests_html import HTML
from werkzeug.datastructures import Headers

import birding
from birding.account import PasswordHasher, Password
from birding.authentication import SaltFactory
from birding.database import Transaction


def mock_return(value):
  return Mock(return_value=value)

def mock_database_transaction():
  transaction = Mock(spec=Transaction)
  transaction.__enter__ = Mock(return_value=transaction)
  transaction.__exit__ = Mock(return_value=None)
  return transaction

class TestClient(FlaskClient):

  def open(self, *args, **kwargs):
    headers = kwargs.pop('headers', Headers())
    kwargs['headers'] = headers
    return super().open(*args, **kwargs)


class AppTestCase(TestCase):

  def setUp(self) -> None:
    test_config = {'TESTING': True, 'SECRET_KEY': 'wowsosecret'}
    self.app = birding.create_app(test_config=test_config)
    self.database = self.app.db
    self.app.test_client_class = TestClient
    self.app_context = self.app.test_request_context()
    self.app_context.push()
    self.client = self.app.test_client()

  def populate_session(self, key, value):
    with self.client.session_transaction() as session:
      session[key] = value

  def assertSessionContains(self, key, value):
    with self.client.session_transaction() as session:
      self.assertIn(key, session)
      self.assertEqual(session[key], value)

  def db_insert_person(self, person_id):
    self.database.query(
      'INSERT INTO person (id, name) VALUES (%s, %s);', (person_id, 'name'))

  def db_insert_locale(self, locale_id, code):
    with self.database.transaction() as transaction:
      transaction.execute(
        'INSERT INTO locale (id, code) VALUES (%s, %s);', (locale_id, code))

  def db_insert_account(self, account_id, username, person_id, locale_id):
    self.app.db.query(
      'INSERT INTO user_account '
      '(id, username, email, person_id, locale_id) '
      'VALUES '
      '(%s, %s, %s, %s, %s);',
      (account_id, username, 'myEmail', person_id, locale_id))

  def db_insert_password(self, account_id, password):
    password_hasher = PasswordHasher(SaltFactory())
    p = Password(password)
    salt_hashed_password = password_hasher.create_salt_hashed_password(p)
    salt = salt_hashed_password[0]
    hashed_password = salt_hashed_password[1]
    self.app.db.query(
      'INSERT INTO hashed_password (user_account_id, salt, salted_hash) '
      'VALUES (%s, %s, %s);', (account_id, salt, hashed_password))

  def db_insert_registration(self, email, token):
    self.app.db.query(
      'INSERT INTO user_account_registration (id, email, token) '
      'VALUES (%s, %s, %s);', (4, email, token))

  def db_insert_bird(self, bird_id, binomial_name):
    self.database.query(
      'INSERT INTO bird (id, binomial_name) '
      'VALUES (%s, %s);', (bird_id, binomial_name))

  def get_flashed_messages(self, category='message'):
    with self.client.session_transaction() as session:
      if '_flashes' in session:
        return dict(session['_flashes']).get(category)

  def set_logged_in(self, account_id):
    self.populate_session('account_id', account_id)

  def assertRedirect(self, response, endpoint):
    self.assertEqual(response.status_code, HTTPStatus.FOUND)
    html = HTML(html=response.data)
    self.assertListEqual(list(html.links), [url_for(endpoint)])

  def tearDown(self) -> None:
    self.database.query('DELETE FROM hashed_password;')
    self.database.query('DELETE FROM user_account;')
    self.database.query('DELETE FROM sighting;')
    self.database.query('DELETE FROM bird;')
    self.database.query('DELETE FROM person;')
    self.database.query('DELETE FROM user_account_registration;')
    with self.database.transaction() as transaction:
      transaction.execute('DELETE FROM locale;')
    self.app_context.pop()
