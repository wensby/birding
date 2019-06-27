#!/bin/sh

while ! nc -z test-database-service 5432; do sleep 1; done

if [ -n "$1" ]; then
  rm .coverage
  rm -rf htmlcov
  coverage run -m unittest discover -s tests
  coverage html
else
  python -m unittest discover -s tests
fi
