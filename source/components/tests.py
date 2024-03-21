import jwt
from config import JWT_SECRET, TEST_USER_ID

print(jwt.decode("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjAxSFJZMlNWU1BaTjRWQUJIOTBTNFZGWjdIIiwicm9sZSI6IkFkbWluIiwiaWF0IjoxNzEwOTM5MDM3LjIxOTUzNSwiZXhwIjoxNzEwOTM5OTM3LjIxOTUzNX0.EYjb1uKEtGifYPGSP7jRewaVfkuqrNER9-KHe2mVzNg", JWT_SECRET, algorithms=["HS256"], options={'verify_signature': False}))

enc_jwt = jwt.encode(payload={'id': TEST_USER_ID, 'role': 'Admin'}, key=JWT_SECRET)

print(enc_jwt)

dec_jwt = jwt.decode(enc_jwt, JWT_SECRET, algorithms=["HS256"])

print(dec_jwt)