## Running the app
- `python manage.py runserver` will not work, because of ASGI
  - use `daphne project_config.asgi:application` instead

Dependencies:
- redis: you to install and run redis server

## Endpoints
### Auth
- account/login
- account/logout
- accounts/register
- accounts/password-reset