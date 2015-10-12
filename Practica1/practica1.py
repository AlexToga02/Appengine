import webapp2
import os
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True
        )

def render_str(template, **params):
    t = JINJA_ENVIRONMENT.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def render(self,template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class MainPage(Handler):
    def get(self):
        diccionario = {}
        diccionario["nombre"] = "Alejandro"
        diccionario["apellido"] = "Perez "

        self.render("index.html", mensaje="Extendiendo la app de App Engine con Jinja",diccionario=diccionario)

application = webapp2.WSGIApplication([('/', MainPage)], debug=True)
