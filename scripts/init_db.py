"""
Database Initialization Script
Creates all tables defined in SQLAlchemy models in the target PostgreSQL database.
"""
import sys
from pathlib import Path

# Add project root and backend to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.core.database import engine, Base
# Import models package to ensure all models are registered on Base.metadata
import app.models  # noqa: F401
from sqlalchemy import inspect


def init_database():
    print("=" * 70)
    print(" INITIALIZING DATABASE TABLES")
    print("=" * 70)
    
    print("Creating all tables from declarative models...")
    Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\nVerified Tables in PostgreSQL:")
    for t in sorted(tables):
        columns = [c["name"] for c in inspector.get_columns(t)]
        print(f"  [TABLE] {t} ({len(columns)} columns: {', '.join(columns[:5])}...)")
        
    print("\n[SUCCESS] Database initialization completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    init_database()
