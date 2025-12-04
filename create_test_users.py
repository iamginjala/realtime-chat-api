"""
Script to create test users in the database for testing.
"""
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if users already exist
    existing_users = User.query.all()

    if existing_users:
        print("\n⚠️  Users already exist in database:")
        print("=" * 50)
        for user in existing_users:
            print(f"ID: {user.id} | Email: {user.email}")
        print("=" * 50)
        print("\n💡 Use these user IDs to generate JWT tokens!")
    else:
        print("\n📝 Creating test users...")

        # Create test users
        user1 = User(
            email='alice@test.com', # type: ignore
            password_hash=generate_password_hash('password123') # type: ignore
        )
        user2 = User(
            email='bob@test.com', # type: ignore
            password_hash=generate_password_hash('password123') # type: ignore
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        print("\n✅ Test users created successfully!")
        print("=" * 50)
        print(f"User 1: ID={user1.id} | Email={user1.email} | Password=password123")
        print(f"User 2: ID={user2.id} | Email={user2.email} | Password=password123")
        print("=" * 50)
        print("\n💡 Next step: Generate JWT tokens for these user IDs!")
