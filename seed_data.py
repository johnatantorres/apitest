import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

sports_data = [
    {"id": 6, "name": "American Football"},
    {"id": 37, "name": "Rugby Union"},
    {"id": 36, "name": "Rugby League"},
    {"id": 3, "name": "Basketball"},
    {"id": 2, "name": "Ice Hockey"},
    {"id": 11, "name": "Baseball"},
    {"id": 1, "name": "Football"},
]

users_data = [
    {"id": 2, "name": "Edward", "sport_id": 1},
    {"id": 3, "name": "Richard", "sport_id": 1},
    {"id": 1, "name": "Juan", "sport_id": 1},
]

def seed_data():
    db = SessionLocal()
    try:
        print("Seeding sports data...")
        for sport in sports_data:
            stmt = text("INSERT INTO sports (id, name) VALUES (:id, :name) ON CONFLICT (id) DO NOTHING;")
            db.execute(stmt, sport)

        print("Seeding users data...")
        for user in users_data:
            stmt = text("INSERT INTO users (id, name, sport_id) VALUES (:id, :name, :sport_id) ON CONFLICT (id) DO NOTHING;")
            db.execute(stmt, user)

        db.commit()
        print("Data seeding successful.")
    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()