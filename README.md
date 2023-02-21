## Running the app
- first run "docker build ."
- then run "docker-compose up"
- then run "docker-compose run web python manage.py migrate"
- then run "docker-compose run web python manage.py createsuperuser"

## Endpoints
### Auth
- account/login
- account/logout
- accounts/register
- accounts/password-reset