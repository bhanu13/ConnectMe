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

"""
The main blog file that implements the functionality of all the pages.


Author - bagarwa2
"""

from verify	import *
from web_template import *
from google.appengine.ext import db
from google.appengine.api import memcache

import logging
import time
import hash_secure as secure
import json

#=============== A Blog Handler =================#


class Blog(Handler):
	def auth(self):
		u = self.read_cookie("username")
		return secure.check_val(str(u))


#================ User Registration ===================#
# The User Object
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

def recent_users(update = False):
	key = "newest_users"
	users = memcache.get(key)
	
	if update or users == None:
		logging.warning("DB QUERY")
		users = db.GqlQuery(" SELECT * FROM User ")
		users = list(users)
		memcache.set(key, users)
	
	return users
		


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

		users = recent_users()
		user = None
		for u in users:
			if u.username == username and u.password == password:
				user = u
				break
		if user:
			user_cookie = secure.hash_val(str(user.username))
			self.set_cookie("username", user_cookie)
			# self.set_cookie("username", user.username)
			# self.redirect('/welcome?username=%s' % user.username)
			self.redirect("/welcome")
		else:
			self.render_main(username = username, error_msg = "Invalid Login Information")


class Welcome(Blog):
	def get(self):

		if self.auth():
			username = self.read_cookie("username")
			username = secure.original_val(username)
			self.render("welcome.html", username = username)

		else:
			self.redirect("/signup")


class SignUp(Handler):

	def render_main(self, error_msg = ""):
		self.render("signup.html", error_msg = error_msg)

	def get(self):
		error_msg = self.request.get("error_msg")
		self.render_main(error_msg)

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

		users = recent_users()
		u = False
		for user in users:
			if user.username == username:
				u = True
		if u:
			msg = 'That user already exists.'
			parameters["error_username"] = msg
			self.render("signup.html", **parameters)
			error = True
			return

		if not valid_password(password):
			parameters["error_password"] = "Not a valid password"
			error = True
			return

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
			recent_users(update = True)
			user_cookie = secure.hash_val(new_user.username)
			self.set_cookie("username", user_cookie)
			self.redirect("/welcome")


class Logout(Handler):

	def get_user(self):
		username = self.read_cookie("username")
		username = secure.original_val(username)
		return username

	def logout(self):
		self.set_cookie("username", "")

	def render_main(self, error_msg = "", logout_msg = ""):
		self.render("logout.html", error_msg = error_msg, logout_msg = logout_msg)

	def get(self):
		msg = self.request.get("error_msg")
		username = self.get_user()
		self.logout()
		if username:
			memcache.delete(username)
		self.render_main(logout_msg = "You have logged out successfully !", error_msg = msg)
		

#==================== Blog Details ======================#
# The Post object

class Post(db.Model):
	author = db.StringProperty(required=True)
	title = db.StringProperty(required=True)
	post = db.TextProperty(required=True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	
	def render(self):
		self.render_text = self.post.replace("\n", "<br>")
		return render_str("post.html", p = self)

	def render_full(self):
		self.render_text = self.post.replace("\n", "<br>")
		return render_str("post_full.html", p = self)

	# Added memcaching
	@classmethod	
	def by_author(cls, author, update = False):
		# posts = Post.all().filter('author =', author).get()
		key = str(author)
		posts = memcache.get(key)

		if posts is None or update:
			logging.warning("DB QUERY")
			posts = db.GqlQuery("SELECT * FROM Post WHERE author = \'%s\' ORDER BY created DESC" % author)
			if posts:
				posts = list(posts)
			memcache.set(key, posts)
		
		return posts
		

	@classmethod
	def by_id(cls, post_id):
		return Post.get_by_id(post_id)

	@classmethod
	def remove_by_id(cls, post_id):
		# key = db.Key.from_path("Post", int(post_id))
		# post = db.get(key)
		post = Post.by_id(post_id)
		if post:
			post.delete()

	def as_dict(self):
		d = {	'author':self.author,
				'title':self.title,
				'post':self.post,
				'created':self.created.strftime('%c'),
				'last_modified':self.last_modified.strftime('%c')
		}
		return d

	# Added memcaching
	@classmethod
	def recent_posts(cls, update = False):
		key = "newest_posts"
		posts = memcache.get(key)

		if posts is None or update:
			logging.warning("DB QUERY")
			posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")

			posts = list(posts)
			memcache.set(key, posts)
		
		return posts


#=======================================================#
class MainPage(Blog):
	def render_main(self):
		posts = Post.recent_posts()
		posts = posts[:10]
		
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
			author = secure.original_val(author)
			self.render_main(author=author)
		else:
			error_msg = "You have an invalid session, please login again"
			self.redirect("/logout?error_msg="+error_msg)

	def post(self):
		# author = self.request.get("author")
		author = self.read_cookie("username")
		author = secure.original_val(author)
		title = self.request.get("title")
		post = self.request.get("post")

		if author and post and title:
			p = Post(author=author, title=title, post=post)
			p.put()
			time.sleep(0.1)
			Post.recent_posts(update = True)
			Post.by_author(author = author, update = True)
			self.redirect("/posts/%s" % str(p.key().id()) )

		else:
			error_msg = "Please fill out all the fields."
			self.render_main(author, title, post, error_msg)


class UserPosts(Blog):

	def get_user(self):
		username = self.read_cookie("username")
		username = secure.original_val(username)
		return username

	def render_main(self, error_msg = ""):
		if self.auth():
			username = self.get_user()
			posts = Post.by_author(author = username)
			self.render("myposts.html", posts = posts, error_msg = error_msg)
		else:
			error_msg = "You have an invalid session, please login again"
			self.redirect("/logout?error_msg="+error_msg)

	def get(self):
		self.render_main()

	def post(self):
		post_id = self.request.get("post")
		if not post_id:
			self.render_main(error_msg = "You didn't select anything")
			return
		Post.remove_by_id(int(post_id))
		post_key = 'POST' + str(post_id)
		memcache.delete(post_key)
		time.sleep(0.1)		# Delay for the Google Data Store to process the request 
		Post.recent_posts(update = True)
		username = self.get_user()
		Post.by_author(author = username, update = True)
		self.render_main()


class IndividualPost(Blog):
	def get(self, post_id):
		log_in = True
		if not self.auth():
			log_in = False
		post_key = 'POST' + post_id
		post = memcache.get(post_key)

		if not post:
			key = db.Key.from_path("Post", int(post_id))
			post = db.get(key)
			logging.warning("DB QUERY")
			memcache.set(post_key, post)

		if not post:
			# self.write("Some Error %s" % post_id)
			self.error(404)
		else:
			self.render("postpage.html", post = post, log_in = log_in)
		# else:
		# 	error = "Please signup or login first to read full post."
		# 	self.redirect("/signup?error_msg=" + error)

#=====================================================#
# Added JSON responses

class JsonHandler(Handler):
	def render_json(self, d):
		json_text = json.dumps(d)
		self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
		self.write(json_text)

class MainPageJson(JsonHandler):	
	def get(self):
		posts = Post.recent_posts()
		posts = posts[:10]
		p_dict = list()
		for p in posts:
			p_dict.append(p.as_dict())
		self.render_json(p_dict)

class PostPageJson(JsonHandler):
	def get(self, post_id):
		# key = db.Key.from_path("Post", int(post_id))
		p = Post.by_id(int(post_id))
		self.render_json(p.as_dict())

#=====================================================#

app = webapp2.WSGIApplication([
    ('/', MainPage), ('/newpost', NewPost), ('/posts/([0-9]+)', IndividualPost), ('/posts/([0-9]+).json', PostPageJson),
    ('/welcome', Welcome), ('/signup', SignUp), ('/login', Login), ('/logout', Logout),
    ('/myposts', UserPosts), ('/.json', MainPageJson) # ('/users', Users)
], debug=True)
