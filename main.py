#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#



from verify	import *
from web_template import *
from google.appengine.ext import db

#================ User Registration ===================#

class User(db.Model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	email = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

	@classmethod
	def by_name(cls, username):
		u = User.all().filter('username =', username).get()
		return u

	@classmethod
	def by_id(cls, uid):
		return User.get_by_id(uid)

#
class Login(Handler):
	def render_main(self, username = "", error_msg = ""):
		self.render("login.html", username = username, error_msg = error_msg)
	
	def get(self):
		self.render_main()

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		if not (valid_username(username) and valid_password(password)):
			self.render_main(error_msg="Please enter a valid username")
			return

		db_user = db.GqlQuery(" SELECT * FROM User WHERE username = \'%s\' AND password = \'%s\' " % (username, password))
		user = db_user.get()	# If this object exists then login complete - Add cookie storage
		if user:
			self.set_cookie("username", user.username)
			# self.redirect('/welcome?username=%s' % user.username)
			self.redirect("/welcome")
		else:
			self.render_main(username = username, error_msg = "Invalid Login Information")


#
class Welcome(Handler):

	def get(self):
		username = self.read_cookie("username")
		if valid_username(username):
			self.render("welcome.html", username = username)
		else:
			self.redirect("/signup")

#


class SignUp(Handler):

	def get(self):
		self.render("signup.html")

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		password2 = self.request.get('password2')
		email = self.request.get('email')
		error = False

		parameters = dict(username = username, email = email)

		if not valid_username(username):
			parameters["error_username"] = "Not a valid username"
			error = True
#
		u = User.by_name(username)
		if u:
			msg = 'That user already exists.'
			parameters["error_username"] = msg
			self.render("signup.html", **parameters)
			error = True
			return

#
		if not valid_password(password):
			parameters["error_password"] = "Not a valid password"
			error = True
		
		if password != password2:
			parameters["error_verify"] = "The passwords don't match"
			error = True

		if not valid_email(email):
			parameters["error_email"] = "That is not a valid email address"
			error = True
		
		if error:
			self.render("signup.html", **parameters)

		else:
			new_user = User(username = username, password = password, email = email)
			new_user.put()
			self.set_cookie("username", new_user.username)
			self.redirect("/welcome")

class Logout(Handler):
	def logout(self):
		self.set_cookie("username", "")

	def render_main(self, error_msg = "", logout_msg = ""):
		self.render("logout.html", error_msg = error_msg, logout_msg = logout_msg)

	def get(self):
		msg = self.request.get("error_msg")
		self.logout()
		self.render_main(logout_msg = "You have logged out successfully !", error_msg = msg)
		
class Users(Handler):
	def get(self):
		users = db.GqlQuery("SELECT * FROM User ORDER BY created DESC")
		self.render("users.html", users = users)

#=============== Blog Display Details =================#


class Blog(Handler):
	def auth(self):
		u = self.read_cookie("username")
		u = User.by_name(u)
		if u:
			return True
		else:
			return False


#======================================================#
class Post(db.Model):
	author = db.StringProperty(required=True)
	title = db.StringProperty(required=True)
	post = db.TextProperty(required=True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	
	def render(self):
		self.render_text = self.post.replace("\n", "<br>")
		return render_str("post.html", p = self)


class MainPage(Blog):
	def render_main(self):
		posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC limit 10 ")
		
		if self.auth():
			self.render("home.html", posts=posts, log_in = True)	# Look into return type if list is empty to add error msg
		else:
			self.render("home.html", posts=posts)

	def get(self):
		self.render_main()


class NewPost(Blog):

	def render_main(self, author="", title="", post="", error_msg=""):
		self.render("newpost.html", author=author, title=title, post=post, error_msg=error_msg)

	def get(self):
		if self.auth():
			author = self.read_cookie("username")
			self.render_main(author=author)
		else:
			error_msg = "You have an invalid session, please login again"
			self.redirect("/logout?error_msg="+error_msg)

	def post(self):
		# author = self.request.get("author")
		author = self.read_cookie("username")
		title = self.request.get("title")
		post = self.request.get("post")

		if author and post and title:
			p = Post(author=author, title=title, post=post)
			p.put()
			self.redirect("/posts/%s" % str(p.key().id()) )

		else:
			error_msg = "Please fill out all the fields."
			self.render_main(author, title, post, error_msg)

class UserPosts(Blog):

	def get(self):
		if self.auth():
			self.write("Hello my Posts are here.")
		else:
			error_msg = "You have an invalid session, please login again"
			self.redirect("/logout?error_msg="+error_msg)


class IndividualPost(Handler):
	def get(self, post_id):
		key = db.Key.from_path("Post", int(post_id))
		post = db.get(key)

		if not post:
			# self.write("Some Error %s" % post_id)
			self.error(404)
		else:
			self.render("postpage.html", post = post)

#=====================================================#


app = webapp2.WSGIApplication([
    ('/', MainPage), ('/newpost', NewPost), ('/posts/([0-9]+)', IndividualPost),
    ('/welcome', Welcome), ('/signup', SignUp), ('/users', Users), ('/login', Login), ('/logout', Logout),
    ('/myposts', UserPosts)
], debug=True)
