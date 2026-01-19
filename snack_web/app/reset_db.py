"""Drop and recreate all database tables.

WARNING: This will delete all data in the database!

Usage:
  - locally: `python -m app.reset_db`
  - in Docker: `docker compose exec web python -m app.reset_db`
"""
from app.core.database import engine, Base

# Import all models so they're registered
from app.modules.users import models as users_models  # noqa: F401
from app.modules.snacks import models as snacks_models  # noqa: F401
from app.modules.stock import models as stock_models  # noqa: F401
from app.modules.sales import models as sales_models  # noqa: F401


def reset_database():
    print("WARNING: This will drop all tables and delete all data!")
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Done! Database reset complete. Run 'python -m app.seed' to populate data.")


if __name__ == "__main__":
    reset_database()
