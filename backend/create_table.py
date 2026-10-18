from sqlalchemy import inspect

from backend.database import engine, Base
import backend.table_model


def recreate_tables():
    inspector = inspect(engine)

    if inspector.has_table("users"):
        print("Warning: Users table already exists.")
        choice = input("Do you want to DROP and recreate it? (y/n): ").strip().lower()

        if choice != "y":
            print("Operation cancelled.")
            return

        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped.")

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


if __name__ == "__main__":
    recreate_tables()
