from http import HTTPStatus

from flask import Response
from flask import g
from flask import request
from flask import make_response
from flask import jsonify

from aveslog.v0.error import ErrorCode
from aveslog.v0.authentication import SaltFactory
from aveslog.v0.rest_api import error_response
from aveslog.v0.rest_api import require_authentication
from aveslog.v0.account import is_valid_username
from aveslog.v0.account import PasswordHasher
from aveslog.v0.account import is_valid_password
from aveslog.v0.models import AccountRegistration, HashedPassword
from aveslog.v0.models import Account
from aveslog.v0.models import Birder


def create_account() -> Response:
  token = request.json.get('token')
  username = request.json.get('username')
  password = request.json.get('password')
  field_validation_errors = validate_fields(password, username)
  if field_validation_errors:
    return validation_failed_error_response(field_validation_errors)
  session = g.database_session
  registration = session.query(AccountRegistration) \
    .filter_by(token=token).first()
  if not registration:
    return registration_request_token_invalid_response()
  if session.query(Account).filter_by(username=username).first():
    return username_taken_response()
  account = Account(username=username, email=registration.email)
  account.hashed_password = create_hashed_password(password)
  account.birder = Birder(name=account.username)
  session.add(account)
  session.delete(registration)
  session.commit()
  json = jsonify(account_representation(account))
  return make_response(json, HTTPStatus.CREATED)


def account_representation(account):
  return {
    'id': account.id,
    'username': account.username,
    'email': account.email,
    'birder': {
      'id': account.birder.id,
      'name': account.birder.name,
    },
  }


def create_hashed_password(password: str) -> HashedPassword:
  salt_factory = SaltFactory()
  password_hasher = PasswordHasher(salt_factory)
  salt, hash = password_hasher.create_salt_hashed_password(password)
  return HashedPassword(salt=salt, salted_hash=hash)


def username_taken_response():
  return error_response(
    ErrorCode.USERNAME_TAKEN,
    'Username taken',
    status_code=HTTPStatus.CONFLICT,
  )


def registration_request_token_invalid_response():
  return error_response(
    ErrorCode.INVALID_ACCOUNT_REGISTRATION_TOKEN,
    'Registration request token invalid',
    status_code=HTTPStatus.BAD_REQUEST,
  )


def validate_fields(password, username):
  errors = []
  if not is_valid_username(username):
    errors.append({
      'code': ErrorCode.INVALID_USERNAME_FORMAT,
      'field': 'username',
      'message': 'Username need to adhere to format: ^[a-z0-9_.-]{5,32}$',
    })
  if not is_valid_password(password):
    errors.append({
      'code': ErrorCode.INVALID_PASSWORD_FORMAT,
      'field': 'password',
      'message': 'Password need to adhere to format: ^.{8,128}$'
    })
  return errors


def validation_failed_error_response(field_validation_errors):
  return error_response(
    ErrorCode.VALIDATION_FAILED,
    'Validation failed',
    additional_errors=field_validation_errors,
  )


@require_authentication
def get_account(username: str):
  session = g.database_session
  account = session.query(Account).filter_by(username=username).first()
  if not account:
    return make_response('', HTTPStatus.NOT_FOUND)
  json = jsonify(account_summary_representation(account))
  return make_response(json, HTTPStatus.OK)


@require_authentication
def get_accounts() -> Response:
  accounts = g.database_session.query(Account).all()
  json = jsonify({'items': list(map(account_summary_representation, accounts))})
  return make_response(json, HTTPStatus.OK)


@require_authentication
def get_me() -> Response:
  account = g.authenticated_account
  json = jsonify(account_summary_representation(account))
  return make_response(json, HTTPStatus.OK)


def account_summary_representation(account: Account):
  return {
    'username': account.username,
    'birderId': account.birder_id
  }