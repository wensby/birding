import json
import os

from birding.database import Database
from .bird import Bird


class Locale:

  def __init__(self, locale_id: int, code: str):
    self.id = locale_id
    self.code = code

  @classmethod
  def from_row(cls, row):
    return cls(row[0], row[1])

  def __repr__(self):
    return f'{self.__class__.__name__}({self.id}, {self.code})'

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self.__dict__ == other.__dict__
    return False

  def __hash__(self):
    return hash(self.id) ^ hash(self.code)


class LoadedLocale:

  def __init__(self, locale: Locale, dictionary: dict, bird_dictionary: dict,
        misses_repository: dict):
    self.locale = locale
    self.dictionary = dictionary
    self.bird_dictionary = bird_dictionary
    self.misses_repository = misses_repository

  def text(self, text, variables=None):
    if self.dictionary and text in self.dictionary:
      translated = self.dictionary[text]
    else:
      if not self.misses_repository is None:
        self.misses_repository[self.locale] = text
      translated = text
    if variables:
      i = 0
      while '{{}}' in translated:
        translated = translated.replace('{{}}', variables[i], 1)
        i = i + 1
    return translated

  def name(self, bird):
    binomial_name = bird.binomial_name if isinstance(bird, Bird) else bird
    if self.bird_dictionary and binomial_name in self.bird_dictionary:
      return self.bird_dictionary[binomial_name]
    else:
      return binomial_name


class LocaleLoader:

  def __init__(self, locales_directory_path):
    self.locales_directory_path = locales_directory_path

  def load_locale(self, locale: Locale) -> LoadedLocale:
    language_dictionary = None
    bird_dictionary = None
    dictionary_filepath = (
      f'{self.locales_directory_path}{locale.code}/{locale.code}.json')
    if os.path.exists(dictionary_filepath):
      with open(dictionary_filepath, 'r') as file:
        language_dictionary = json.load(file)
    bird_dictionary_filepath = (
      f'{self.locales_directory_path}/{locale.code}/{locale.code}-bird-names.json')
    if os.path.exists(bird_dictionary_filepath):
      with open(bird_dictionary_filepath, 'r') as file:
        bird_dictionary = json.load(file)
    return LoadedLocale(locale, language_dictionary, bird_dictionary, None)

class LocaleRepository:

  def __init__(self, locales_directory_path, locale_loader: LocaleLoader, database: Database):
    self.locales_directory_path = locales_directory_path
    self.locale_loader = locale_loader
    self.database = database

  def available_locale_codes(self):
    def is_length_2(x):
      return len(x) == 2
    def locales_directory_subdirectories():
      path = self.locales_directory_path
      return filter(lambda x: os.path.isdir(path + x), os.listdir(path))
    return list(filter(is_length_2, locales_directory_subdirectories()))

  def enabled_locale_codes(self):
    with self.database.transaction() as transaction:
      result = transaction.execute('SELECT id, code FROM locale;')
      return list(map(lambda x: x[1], result.rows))

  def find_locale_by_id(self, id) -> Locale:
    with self.database.transaction() as transaction:
      result = transaction.execute('SELECT code FROM locale WHERE id = %s;',
                                   (id,))
      return self.find_locale_by_code(result.rows[0][0])

  def find_locale_by_code(self, code) -> Locale:
    with self.database.transaction() as transaction:
      result = transaction.execute(
        'SELECT id, code FROM locale WHERE code LIKE %s;', (code,),
        Locale.from_row)
      return next(iter(result.rows), None)

  @property
  def locales(self):
    with self.database.transaction() as transaction:
      result = transaction.execute(
        'SELECT id, code FROM locale;', mapper=Locale.from_row)
      return result.rows


class LocaleDeterminerFactory:

  def __init__(self,
        user_locale_cookie_key: str,
        locale_repository : LocaleRepository):
    self.user_locale_cookie_key = user_locale_cookie_key
    self.locale_repository = locale_repository

  def create_locale_determiner(self):
    available = self.locale_repository.available_locale_codes()
    enabled = self.locale_repository.enabled_locale_codes()
    locale_codes = list(filter(lambda locale: locale in enabled, available))
    return LocaleDeterminer(self.user_locale_cookie_key, locale_codes)

class LocaleDeterminer:

  def __init__(self,
        user_locale_cookie_key,
        locale_codes: list):
    self.user_locale_cookie_key = user_locale_cookie_key
    self.locale_codes = locale_codes

  def determine_locale_from_request(self, request):
    if not self.locale_codes:
      return None
    locale_code = self.__determine_from_cookies(request.cookies)
    if not locale_code:
      locale_code = self.__determine_from_headers(request.headers)
    if not locale_code:
      locale_code = next(iter(self.locale_codes), None)
    return locale_code

  def __determine_from_cookies(self, cookies):
    cookie_locale_code = cookies.get(self.user_locale_cookie_key)
    if cookie_locale_code in self.locale_codes:
      return cookie_locale_code

  def __determine_from_headers(self, headers):
    if 'Accept-Language' in headers:
      header = headers['Accept-Language']
      requested_codes = list(map(lambda c: c.split(';')[0], header.split(',')))
      matching_codes = filter(lambda c: c in self.locale_codes, requested_codes)
      return next(matching_codes, None)