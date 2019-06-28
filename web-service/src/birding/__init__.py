import os
from flask import Flask
from flask import g
from flask import request
from flask import after_this_request
from flask import redirect
from flask import url_for
from .database import DatabaseFactory
from .account import AccountRepository
from .account import PasswordHasher
from .authentication import Authenticator
from .account import PasswordRepository
from .account import TokenFactory
from .mail import MailDispatcherFactory
from .person import PersonRepository
from .blueprint_home import create_home_blueprint
from .blueprint_authentication import create_authentication_blueprint
from .blueprint_search import create_search_blueprint
from .sighting_blueprint import create_sighting_blueprint
from .blueprint_profile import create_profile_blueprint
from .blueprint_settings import create_settings_blueprint
from .blueprint_bird import create_bird_blueprint
from .localization import LocaleDeterminer
from .localization import LocalesFactory
from .bird import BirdRepository
from .search import BirdSearcher
from .search import BirdSearchController
from .search import StringMatcher
from .sighting import SightingRepository
from .picture import PictureRepository
from .search_view import BirdSearchViewFactory
from .sighting_view import SightingViewFactory
from .authentication import AccountRegistrationController
from .authentication import PasswordResetController
from .authentication import SaltFactory
from .link import LinkFactory
from .bird_view import BirdViewFactory


def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  configure_app(app, test_config)

  # Create blueprint dependencies
  user_locale_cookie_key = 'user_locale'
  database_connection_factory = DatabaseFactory(app.logger)
  database_connection_details = create_database_connection_details()
  database = database_connection_factory.create_database(**database_connection_details)
  app.db = database
  salt_factory = SaltFactory()
  hasher = PasswordHasher(salt_factory)
  token_factory = TokenFactory()
  account_repository = AccountRepository(database, hasher, token_factory)
  mail_dispatcher_factory = MailDispatcherFactory(app)
  mail_dispatcher = mail_dispatcher_factory.create_dispatcher()
  person_repository = PersonRepository(database)
  authenticator = Authenticator(account_repository, hasher)
  localespath = os.path.join(app.root_path, 'locales/')
  locales_factory = LocalesFactory(database, localespath)
  locales = locales_factory.create_locales()
  locale_determiner = LocaleDeterminer(locales, user_locale_cookie_key)
  bird_repository = BirdRepository(database)
  string_matcher = StringMatcher()
  bird_searcher = BirdSearcher(bird_repository, locales, string_matcher)
  sighting_repository = SightingRepository(database)
  picture_repository = PictureRepository(database)
  bird_search_view_factory = BirdSearchViewFactory(picture_repository, bird_repository)
  sighting_view_factory = SightingViewFactory(bird_repository, database)
  link_factory = LinkFactory(os.environ['EXTERNAL_HOST'])
  account_registration_controller = AccountRegistrationController(account_repository, mail_dispatcher, link_factory,
                                                                  person_repository)
  bird_view_factory = BirdViewFactory(bird_repository, picture_repository)
  bird_search_controller = BirdSearchController(bird_searcher)
  password_repository = PasswordRepository(token_factory, database, hasher)
  password_reset_controller = PasswordResetController(
    account_repository, password_repository, link_factory, mail_dispatcher)

  # Create and register blueprints
  home_blueprint = create_home_blueprint()
  authentication_blueprint = create_authentication_blueprint(
    account_repository,
    authenticator,
    account_registration_controller,
    password_reset_controller,
  )
  search_blueprint = create_search_blueprint(bird_search_controller, bird_search_view_factory)
  sighting_blueprint = create_sighting_blueprint(sighting_repository, sighting_view_factory)
  profile_blueprint = create_profile_blueprint(account_repository)
  settings_blueprint = create_settings_blueprint(account_repository, authenticator, password_repository)
  bird_blueprint = create_bird_blueprint(bird_view_factory)
  app.register_blueprint(home_blueprint)
  app.register_blueprint(authentication_blueprint)
  app.register_blueprint(search_blueprint)
  app.register_blueprint(sighting_blueprint)
  app.register_blueprint(profile_blueprint)
  app.register_blueprint(settings_blueprint)
  app.register_blueprint(bird_blueprint)

  @app.before_request
  def before_request():
    # initialize render context dictionary
    g.render_context = dict()
    detect_user_locale()

  def detect_user_locale():
    locale = locale_determiner.determine_locale_from_request(request)
    update_locale_context(locale)

  def update_locale_context(locale):
    previously_set = request.cookies.get(user_locale_cookie_key, None)
    # when the response exists, set a cookie with the language if it is new
    if locale.language and (not previously_set or previously_set is not locale.language.iso_639_1_code):
      set_locale_cookie_after_this_request(locale)
    g.locale = locale
    g.render_context['locale'] = locale

  def set_locale_cookie_after_this_request(locale):
    @after_this_request
    def remember_language(response):
      response.set_cookie(user_locale_cookie_key, locale.language.iso_639_1_code)
      return response

  @app.route('/language')
  def language():
    language_code = request.args.get('l')
    languages = list(filter(lambda l: l.iso_639_1_code == language_code, locales))
    if languages:
      language = languages[0]
      locale = locales[language]
      update_locale_context(locale)
      return redirect(url_for('index'))

  app.logger.info('Flask app constructed')
  return app


def configure_app(app, test_config):
  if not os.path.isdir(app.instance_path):
    os.makedirs(app.instance_path)
  if test_config:
    app.config.from_mapping(test_config)
  else:
    app.config.from_pyfile('config.py', silent=True)
  if not app.config['SECRET_KEY']:
    raise Exception('Flask secret key not set')


def create_database_connection_details():
  return {
    'host': os.environ.get('DATABASE_HOST'),
    'dbname': os.environ.get('DATABASE_NAME'),
    'user': os.environ.get('DATABASE_USER'),
    'password': os.environ.get('DATABASE_PASSWORD')
  }
