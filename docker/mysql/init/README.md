# MySQL container

The MySQL service uses a persistent Docker named volume.

The application database is created from the MYSQL_DATABASE environment
variable when the MySQL data directory is first initialized.

Flask-Migrate/Alembic migrations are deliberately NOT run automatically
during container startup. Apply migrations explicitly after confirming
the database target:

    docker compose exec web flask --app app.py db upgrade

Do not delete the database volume to troubleshoot startup problems.