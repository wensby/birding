from flask import Blueprint
from birding.birds_rest_api import BirdsRestApi
from .routes import create_birds_routes


def create_api_v0_blueprint(birds_rest_api: BirdsRestApi) -> Blueprint:
  blueprint = Blueprint('v0', __name__)

  def register_routes(routes):
    for route in routes:
      rule = route['rule']
      endpoint = route.get('endpoint', None)
      view_func = route['view_func']
      options = route.get('options', {})
      blueprint.add_url_rule(rule, endpoint, view_func, **options)
      blueprint.add_url_rule(f'/v0{rule}', endpoint, view_func, **options)

  birds_routes = create_birds_routes(birds_rest_api)
  register_routes(birds_routes)
  return blueprint