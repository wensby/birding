from hashlib import pbkdf2_hmac
from base64 import b64encode, b64decode
import binascii
import os
import re

username_regex = re.compile('^[A-z]{1,20}$')
password_regex = re.compile('^[A-z]{1,20}$')

def is_valid_username(username):
  return username_regex.match(username)

def is_valid_password(password):
  return password_regex.match(password)

class UserAccount:

  def __init__(self, id, username, email, person_id, locale_id):
    self.id = id
    self.username = username
    self.email = email
    self.person_id = person_id
    self.locale_id = locale_id

class UserAccountRegistration:

  def __init__(self, id, email, token):
    self.id = id
    self.email = email
    self.token = token

class Credentials:

  def __init__(self, username, password):
    if not is_valid_username(username):
      raise Exception("invalid username format")
    if not is_valid_password(password):
      raise Exception("invalid password format")
    self.username = username
    self.password = password

  def is_valid(username, password):
    return is_valid_username(username) and is_valid_password(password)

class HashedPassword:

  def __init__(self, user_account_id, salt, salted_hash):
    self.user_account_id = user_account_id
    self.salt = salt
    self.salted_hash = salted_hash

class UserAccountRepository:

  def __init__(self, database, password_hasher):
    self.database = database
    self.hasher = password_hasher

  def remove_user_account_registration_by_id(self, id):
    query = ('DELETE FROM user_account_registration '
             'WHERE id = %s;')
    self.database.query(query, (id,))

  def put_user_account_registration(self, email):
    if not self.get_user_account_registration_by_email(email):
      token = os.urandom(16).hex()
      query = ('INSERT INTO user_account_registration (email, token) '
               'VALUES (%s, %s);')
      self.database.query(query, (email, token))

  def get_user_account_registration_by_email(self, email):
    query = ('SELECT id, email, token '
             'FROM user_account_registration '
             'WHERE email LIKE %s;')
    rows = self.database.query(query, (email,))
    if rows:
      return UserAccountRegistration(rows[0][0], rows[0][1], rows[0][2])

  def get_user_account_registration_by_token(self, token):
    query = ('SELECT id, email, token '
             'FROM user_account_registration '
             'WHERE token LIKE %s;')
    rows = self.database.query(query, (token,))
    if rows:
      return UserAccountRegistration(rows[0][0], rows[0][1], rows[0][2])

  def get_user_account_by_id(self, id):
    query = ('SELECT id, username, email, person_id, locale_id '
             'FROM user_account '
             'WHERE id = %s;')
    rows = self.database.query(query, (id,))
    if rows:
      return UserAccount(rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4])

  def find_user_account(self, username):
    query = ('SELECT id, username, email, person_id, locale_id '
             'FROM user_account '
             'WHERE username LIKE %s;')
    rows = self.database.query(query, (username,))
    if rows:
      return UserAccount(rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4])

  def find_hashed_password(self, user_account):
    query = ('SELECT user_account_id, salt, salted_hash '
             'FROM hashed_password '
             'WHERE user_account_id = %s;')
    rows = self.database.query(query, (user_account.id,))
    if rows:
      return HashedPassword(rows[0][0], rows[0][1], rows[0][2])

  def put_new_user_account(self, email, username, password):
    if not Credentials.is_valid(username, password):
      return None
    if not self.find_user_account(username):
      query = ('INSERT INTO user_account (username, email) '
               'VALUES (%s, %s);')
      self.database.query(query, (username, email))
      account = self.find_user_account(username)
      if not account:
        return
      salt = b64encode(os.urandom(16)).decode('utf-8')
      hash = self.hasher.hash_password(password, salt)
      query = ('INSERT '
               'INTO hashed_password (user_account_id, salt, salted_hash) '
               'VALUES (%s, %s, %s);')
      self.database.query(query, (account.id, salt, hash))
      if self.find_hashed_password(account):
        return account

  def set_user_account_person(self, account, person):
    query = ('UPDATE user_account '
             'SET person_id = %s '
             'WHERE id = %s;')
    self.database.query(query, (person.id, account.id))

class PasswordHasher:

  def hash_password(self, password, salt):
    encoded_password = password.encode()
    encoded_salt = salt.encode()
    binary_hash = pbkdf2_hmac('sha256', encoded_password, encoded_salt, 100000)
    return binascii.hexlify(binary_hash).decode()

class Authenticator:

  def __init__(self, user_account_repository, password_hasher):
    self.account_repository = user_account_repository
    self.hasher = password_hasher

  def get_authenticated_user_account(self, credentials):
    username = credentials.username
    password = credentials.password
    account = self.account_repository.find_user_account(username)
    if account:
      hashed_password = self.account_repository.find_hashed_password(account)
      if hashed_password:
        salt = hashed_password.salt
        expected_hash = hashed_password.salted_hash
        if self.hasher.hash_password(password, salt) == expected_hash:
          return account