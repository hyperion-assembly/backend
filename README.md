![ha_landscape](https://github.com/hyperion-assembly/backend/assets/686075/37d7b6d1-4e6c-4eba-84eb-3255122ca756)

# Hyperion Assembly backend [![CI](https://github.com/hyperion-assembly/backend/actions/workflows/ci.yml/badge.svg)](https://github.com/hyperion-assembly/backend/actions/workflows/ci.yml)

backend for hyperion assembly

## Setup

Create a .env file with your configuration. See .env.example for an example.

```bash
brew install postgresql pipenv pyenv pre-commit
```
Download, install and run Postgres version 15
e.g. for Mac: https://postgresapp.com  

```bash
pyenv install 3.10
pipenv install
psql -c 'create database hyperion_backend_dev;'
pre-commit install
pipenv shell
python manage.py migrate
python manage.py runserver
```
Now you can visit 
`http://127.0.0.1:8000/admin/`
to login to the local Hyperion Admin page.
To login follow `Setting up your user account` below

## Basic Commands

### Setting up your user account
Create a **superuser account** with this command:

```bash
python manage.py createsuperuser
```

### Type checks

Running type checks with mypy:

```bash
mypy hyperion_backend
```

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:
```bash
coverage run -m pytest
coverage html
open htmlcov/index.html
```

#### Running tests with pytest

```bash
pytest
```

#### Testing Github Webhooks with local server

```bash
DJANGO_READ_DOT_ENV_FILE=True python manage.py runserver
smee -p 8000 -P "/callbacks/github"
```

## Deployment

```bash
chmod +x zappa_deploy.sh
./zappa_deploy.sh
```
