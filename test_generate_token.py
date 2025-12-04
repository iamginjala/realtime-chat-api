"""
Generate JWT tokens for test users.
Run this after creating test users with create_test_users.py
"""
from utils.jwt_helper import generate_token
import sys

if len(sys.argv) > 1:
    # Generate token for specific user ID
    user_id = int(sys.argv[1])
    email = sys.argv[2] if len(sys.argv) > 2 else f"user{user_id}@test.com"
    token = generate_token(user_id, email)
    print(f"\n✅ JWT Token for User {user_id} ({email}):")
    print("=" * 80)
    print(token)
    print("=" * 80)
else:
    # Generate tokens for default test users
    print("\n🔑 Generating JWT Tokens for Test Users")
    print("=" * 80)

    token1 = generate_token(1, 'alice@test.com')
    print(f"\n👤 User 1 (Alice - ID: 1):")
    print(token1)

    token2 = generate_token(2, 'bob@test.com')
    print(f"\n👤 User 2 (Bob - ID: 2):")
    print(token2)

    print("\n" + "=" * 80)
    print("💡 Copy these tokens to use in test_client.html")
    print("=" * 80)