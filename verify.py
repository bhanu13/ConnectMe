"""
Basic Verification Code for username, password and email ID

"""

import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,15}$")
def valid_username(username):
	return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,15}$")
def valid_password(password):
	return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
	return email and EMAIL_RE.match(email)