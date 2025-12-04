"""
Script to drop all tables and recreate them.
WARNING: This will delete all data in the database!
"""
from app import create_app
from models import db

app = create_app()

with app.app_context():
    print("\n⚠️  WARNING: This will delete all existing data!")
    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() == 'yes':
        print("\n🗑️  Dropping all tables...")
        db.drop_all()
        print("✅ All tables dropped")

        print("\n📝 Creating tables with correct schema...")
        db.create_all()
        print("✅ All tables created successfully!")

        print("\n📋 Tables created:")
        print("  - users")
        print("  - conversations")
        print("  - messages")

        print("\n💡 Next steps:")
        print("  1. Run: python create_test_users.py")
        print("  2. Run: python test_generate_token.py")
        print("  3. Test with test_client.html")
    else:
        print("\n❌ Operation cancelled")
