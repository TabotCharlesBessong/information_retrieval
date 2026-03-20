# Alembic Migrations (Pipeline)

This folder contains SQLAlchemy/Alembic migration history for the Phase B pipeline schema.

## Quickstart

From app/pipeline:

1. Install dependencies:
- pip install -r requirements.txt

2. Generate migration from model changes:
- alembic revision --autogenerate -m "describe change"

3. Apply latest migrations:
- alembic upgrade head

4. Roll back one revision:
- alembic downgrade -1

## Notes

1. Database URL is resolved from pipeline environment vars through src/db.py.
2. ORM metadata source is src/models.py.
3. app/pipeline/sql/schema.sql remains in repo as SQL reference and is not removed.
