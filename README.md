# nollesystemet
Web-based system for handling account-based event registration and event form creation. Using Django.


## Pull project
- Pull this repo.
- Create a mariaDB database on your local machine.
- Copy ```Database/db_info_template.cnf``` and name it ```Database/db_info.cnf```. Populate this with your database credentials.
- Populate the database with the latest tables by running ```python manage.py migrate```.
- Add a key file at /etc/django/secret_key.cnf