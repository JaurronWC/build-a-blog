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
		
		
class Index(Handler):

	blog_posts = db.GqlQuery("SELECT * FROM Posts "
							"ORDER BY created DESC ")
	
	def get(self):
		t = jinja_env.get_template("front.html")
        content = t.render()
        self.response.write(content)

			
class Blog(Handler):
	def render_blog(self, title="", post="", error=""):
		posts = db.GqlQuery("SELECT * FROM Post "
							"ORDER BY created DESC ")
	
		self.render("front.html", title=title, post=post, error=error, posts=posts)

	def get(self):
		self.render_front()
		
	def post(self):
		title = self.request.get("title")
		post = self.request.get("post")
		
		if title and post:
			a = Post(title = title, post = post)
			a.put()
			
			self.redirect("/")
		else:
			error = "we need both a title and a blog post!"
			self.render_front(title, post, error = error)

class NewPosts(Handler): 
	def render_newposts(self, title="", post="", error=""):
		posts = db.GqlQuery("SELECT * FROM Post "
							"ORDER BY created DESC ")
							
		self.render("newposts.html", title=title, post=post, error=error, posts=posts)
	
	def get(self):
		self.render_newposts()
		
	def post(self):
		title = self.request.get("title")
		post = self.request.get("post")
		
		if title and post:
			a = Post(title = title, post = post)
			a.put()
			
			self.redirect("/blog")
		else:
			error = "You need to put in both a title and some content"
			self.render_front(title, post, error = error)

 
app = webapp2.WSGIApplication([
	('/', Index),
	('/blog', Blog),
	('/newpost', NewPosts)
], debug=True)
