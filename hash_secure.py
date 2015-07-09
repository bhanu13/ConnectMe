"""
Useful functions for creating secure hashes to store passwords and set cookies.

"""

import hmac
import hashlib
import random
from string import letters

key = "mykey"

def check_val(value):
	if value:
		v = original_val(value)
		v = hash_val(v)
		if v == value:
			return True
		else:
			return False

def hash_val(value):
	if value:
		hash_val = hmac.new(value, key).hexdigest()
		return str(value + "|" + hash_val)

def original_val(value):
	return str(value.split("|")[0])

def create_salt(length = 5):
	salt = ""
	for i in range(0, length):
		salt +=(random.choice(letters))
	return salt

def create_password(password, salt = None):
	if password:
		if not salt:
			salt = create_salt()
		hash_val = hashlib.sha256(password + salt).hexdigest()
		val = salt + "," + hash_val
		return val

def check_password(password, hash_password):
	if hash_password and password:
		salt = get_salt(hash_password)
		val = create_password(password, salt)
		return val == hash_password


def get_salt(value = None):
	if value:
		return str(value.split(",")[0])

# val = hash_val("bhanu")

# print check_val(val)
# print create_salt()
# password = create_password("bhanu")
# print password

# print check_password("bhanu", password)
