from utils.jwt_helper import generate_token

# Generate test tokens
token1 = generate_token(1, 'alice@test.com')
token2 = generate_token(2, 'bob@test.com')

print("Test Tokens:")
print(f"\nUser 1 (alice): {token1}")
print(f"\nUser 2 (bob): {token2}")