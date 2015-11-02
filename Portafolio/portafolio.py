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
        m = "Hola Mundo"
        self.render("index.html", mensaje=m)

class UnidadUno(Handler):
    def get(self):
        self.render("unit1.html")


class UnidadDos(Handler):
    def get(self):
        self.render("unit2.html")

class UnidadTres(Handler):
    def get(self):
        self.render("unit3.html")

class Profile(Handler):
    def get(self):
        self.render("perfil.html")

app = webapp2.WSGIApplication([
                        ('/', MainPage),
                        ('/unidadI',UnidadUno),
			('/unidadII',UnidadDos),
            ('/unidadIII',UnidadTres),
			('/profile',Profile)
], debug=True)
