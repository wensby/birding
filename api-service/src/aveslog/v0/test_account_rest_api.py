import datetime
from http import HTTPStatus
from datetime import timedelta

from flask import Response

from aveslog.v0.authentication import AuthenticationTokenFactory, JwtFactory
from aveslog.test_util import AppTestCase
from aveslog.v0.error import ErrorCode


class TestGetActiveAccounts(AppTestCase):

  def test_get_active_accounts_ok_when_authenticated(self):
    self.db_setup_account(1, 1, 'hulot', 'password', 'hulot@mail.com')

    response = self.get_with_access_token('/accounts', account_id=1)

    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertDictEqual(response.json, {
      'items': [
        {
          'username': 'hulot',
          'birderId': 1,
        },
      ],
    })


class TestAccount(AppTestCase):

  def setUp(self) -> None:
    super().setUp()
    secret_key = self._app.secret_key
    time_supplier = datetime.datetime.utcnow
    jwt_factory = JwtFactory(secret_key)
    self.token_factory = AuthenticationTokenFactory(jwt_factory, time_supplier)

  def test_get_account_when_authenticated_account_disappears(self):
    token = self.token_factory.create_access_token(1)

    response = self.get_own_account(token.jwt)

    self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
    self.assertEqual(response.json, {
      'code': ErrorCode.ACCOUNT_MISSING,
      'message': 'Authorized account gone',
    })

  def test_get_account_when_no_authentication_token(self):
    response = self.get_own_account(None)

    self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
    self.assertDictEqual(response.json, {
      'code': ErrorCode.AUTHORIZATION_REQUIRED,
      'message': 'Authorization required',
    })

  def test_get_account_when_access_token_invalid(self):
    response = self.get_own_account('invalid')

    self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
    self.assertDictEqual(response.json, {
      'code': ErrorCode.ACCESS_TOKEN_INVALID,
      'message': 'Access token invalid',
    })

  def test_get_account_when_access_token_expired(self):
    self.db_setup_account(1, 1, 'hulot', 'myPassword', 'hulot@mail.com')
    expiration = timedelta(seconds=-1)
    token = self.token_factory.create_access_token(1, expiration)

    response = self.get_own_account(token.jwt)

    self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
    self.assertDictEqual(response.json, {
      'code': ErrorCode.ACCESS_TOKEN_EXPIRED,
      'message': 'Access token expired',
    })

  def test_get_account_when_access_token_ok(self):
    self.db_setup_account(1, 1, 'hulot', 'myPassword', 'hulot@mail.com')
    token = self.token_factory.create_access_token(1)

    response = self.get_own_account(token.jwt)

    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertDictEqual(response.json, {
      'username': 'hulot',
      'birderId': 1,
    })

  def get_own_account(self, token):
    if not token:
      return self.client.get('/account')
    else:
      return self.client.get('/account', headers={'accessToken': token})


class TestCreateAccount(AppTestCase):

  def test_post_account_when_credentials_ok(self):
    cursor = self.database_connection.cursor()
    cursor.execute('ALTER SEQUENCE account_id_seq RESTART WITH 1')
    cursor.execute('ALTER SEQUENCE birder_id_seq RESTART WITH 1')
    self.database_connection.commit()
    self.db_insert_registration('hulot@mail.com', 'myToken')

    response = self.post_account('myToken', 'my_username', 'myPassword')

    self.assertEqual(response.status_code, HTTPStatus.CREATED)
    self.assertDictEqual(response.json, {
      'id': 1,
      'username': 'my_username',
      'email': 'hulot@mail.com',
      'birder': {
        'id': 1,
        'name': 'my_username',
      },
    })
    refresh_token_response = self.client.post(
      '/authentication/refresh-token?username=my_username&password=myPassword')
    self.assertEqual(refresh_token_response.status_code, HTTPStatus.CREATED)

  def test_post_account_when_registration_request_missing(self):
    response = self.post_account('myToken', 'my_username', 'myPassword')

    self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    self.assertDictEqual(response.json, {
      'code': ErrorCode.INVALID_ACCOUNT_REGISTRATION_TOKEN,
      'message': 'Registration request token invalid',
    })

  def test_post_account_when_credentials_format_invalid(self):
    response = self.post_account('myToken', 'tiny', 'short')
    self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    self.assertDictEqual(response.json, {
      'code': ErrorCode.VALIDATION_FAILED,
      'message': 'Validation failed',
      'errors': [
        {
          'code': ErrorCode.INVALID_USERNAME_FORMAT,
          'field': 'username',
          'message': 'Username need to adhere to format: ^[a-z0-9_.-]{5,32}$'
        },
        {
          'code': ErrorCode.INVALID_PASSWORD_FORMAT,
          'field': 'password',
          'message': 'Password need to adhere to format: ^.{8,128}$'
        },
      ]
    })

  def test_post_account_when_username_already_taken(self):
    self.db_setup_account(1, 1, 'hulot', 'myPassword', 'hulot@mail.com')
    self.db_insert_registration('new@mail.com', 'token')

    response = self.post_account('token', 'hulot', 'password')

    self.assertEqual(response.status_code, HTTPStatus.CONFLICT)
    self.assertDictEqual(response.json, {
      'code': ErrorCode.USERNAME_TAKEN,
      'message': 'Username taken',
    })

  def post_account(self,
        token: str,
        username: str,
        password: str) -> Response:
    resource = f'/accounts'
    json = {'token': token, 'username': username, 'password': password}
    return self.client.post(resource, json=json)


class TestGetSingleAccount(AppTestCase):

  def test_get_single_account(self):
    self.db_setup_account(1, 1, 'hulot', 'password', 'hulot@mail.com')

    response = self.get_with_access_token('/accounts/hulot', account_id=1)

    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertDictEqual(response.json, {
      'username': 'hulot',
      'birderId': 1,
    })
