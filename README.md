# hyperion assembly backend

backend for hyperion assembly

## Setup

Create a .env file with your configuration. See .env.example for an example.


brew install pipenv
https://postgresapp.com - use version 15

pipenv install
pre-commit install
createdb --username=postgres hyperion_backend
python manage.py migrate

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

```bash
python manage.py createsuperuser
```

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

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
