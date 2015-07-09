"""
A simple template for making webapps on GAE.

Author - bagarwa2, Updated - 08/07/15

"""

import os
import webapp2
import jinja2


#=============== Basic Template Setup =================#

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(templates_dir), autoescape = True)

def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

class Handler(webapp2.RequestHandler):

	def set_cookie(self, name, val):
		q = '%s=%s; Path=/' % (name, val)
		self.response.headers.add_header(
		'Set-Cookie', str(q))

	def read_cookie(self, name):
		cookie_value = self.request.cookies.get(name)
		return cookie_value

	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	
	def render_html(self, template, **parameters):
		tmp = jinja_env.get_template(template)
		return tmp.render(parameters)
	
	def render(self, template, **kw):
		self.write(self.render_html(template, **kw))