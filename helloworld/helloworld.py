import webapp2
import os
import urllib
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def render_str(template, **params):
    t = JINJA_ENVIRONMENT.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


class MainPage(Handler):
    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.write('Hello, World!')
        m = "Hola Mundo"
        self.render("index.html", mensaje=m)

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
