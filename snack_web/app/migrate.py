"""Create database tables from SQLAlchemy models.

This script uses the package layout and imports moved models so
`Base.metadata` contains all table definitions.

Usage:
  - locally: `python -m app.migrate`
  - in Docker container: `docker compose exec web python -m app.migrate`
"""
from app.core.database import engine, Base

# Import modules so SQLAlchemy models are registered on Base.metadata
from app.modules.users import models as users_models  # noqa: F401
from app.modules.snacks import models as snacks_models  # noqa: F401
from app.modules.stock import models as stock_models  # noqa: F401
from app.modules.sales import models as sales_models  # noqa: F401


def migrate():
    print("Creating tables using engine:", engine)
    Base.metadata.create_all(bind=engine)
    print("Done: tables created (if not existing)")


if __name__ == "__main__":
    migrate()
