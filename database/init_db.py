import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from auth.models import Base, engine, SessionLocal, User


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    seed_users()


def seed_users():
    db = SessionLocal()

    test_users = [
        {"username": "alice", "password": "alice123", "role": "hr"},
        {"username": "bob",   "password": "bob123",   "role": "finance"},
        {"username": "carol", "password": "carol123", "role": "marketing"},
        {"username": "dave",  "password": "dave123",  "role": "engineering"},
        {"username": "eve",   "password": "eve123",   "role": "c_level"},
    ]

    for user_data in test_users:
        existing = db.query(User).filter_by(username=user_data["username"]).first()
        if not existing:
            hashed = bcrypt.hashpw(
                user_data["password"].encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")
            user = User(
                username=user_data["username"],
                password_hash=hashed,
                role=user_data["role"]
            )
            db.add(user)
            print(f"  Created user: {user_data['username']} ({user_data['role']})")
        else:
            print(f"  User already exists: {user_data['username']}")

    db.commit()
    db.close()
    print("Seeding complete.")


if __name__ == "__main__":
    init_db()
