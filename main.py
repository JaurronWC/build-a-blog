import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Posts(db.Model):
	title = db.StringProperty(required = True)
	post = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
		
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
		
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
		
		
class MainPage(Handler):
	def render_front(self, title="", post="", error=""):
		posts = db.GqlQuery("SELECT * FROM Posts "
							"ORDER BY created DESC ")
	
		self.render("base.html", title=title, post=post, error=error, posts=posts)

	def get(self):
		self.render_front()
		
	def post(self):
		title = self.request.get("title")
		post = self.request.get("post")
		
		if title and post:
			p = Posts(title = title, post = post)
			p.put()
			
			self.redirect("/")
		else:
			error = "we need both a title and a post!!"
			self.render_front(title, post, error = error)
			
class NewPost(Handler):
	def render_post(self, title="", post="", error=""):
		posts = db.GqlQuery("SELECT * FROM Posts "
							"ORDER BY created DESC ")
	
		self.render("newposts.html", title=title, post=post, error=error, posts=posts)

	def get(self):
		self.render_post()
		
	def post(self):
		title = self.request.get("title")
		post = self.request.get("post")
		
		if title and post:
			p = Posts(title = title, post = post)
			p.put()
			
			id = p.key().id()
			self.redirect("/blog/%s" % id) 
		else:
			error = "we need both a title and a post!!"
			self.render_post(title, post, error = error)
			
class Blog(Handler):
	def render_blog(self, title="", post="", error=""):
		posts = db.GqlQuery("SELECT * FROM Posts "
							"ORDER BY created DESC "
							"LIMIT 5")
	
		self.render("blog.html", title=title, post=post, error=error, posts=posts)

	def get(self):
		self.render_blog()
		
class ViewPostHandler(webapp2.RequestHandler):

	def get(self, id):
		post = Posts.get_by_id(int(id))
		
		if post:
			t = jinja_env.get_template("front.html")
			response = t.render(post=post)
			self.response.out.write(response)
		else:
			error = "That's an invalid ID!"
			self.response.write(error)
		

	
app = webapp2.WSGIApplication([
	('/', MainPage),
	('/newpost', NewPost),
	('/blog', Blog),
	webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
