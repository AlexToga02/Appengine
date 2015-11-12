import webapp2
import os
import jinja2

from webapp2_extras import sessions


template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')


jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request
        self.session_store = sessions.get_store(request=self.request)

        try:
            #Dispatch the request
            webapp2.RequestHandler.dispatch(self)
        finally:
            #save all sessions
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        #returns a session using the default cookie key
        return self.session_store.get_session()

    def render(self, template, **kw):
		self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class AdminHandler(Handler):
    def get(self):
        self.render("paginaadmin.html")

class Messageadmin(Handler):
    def get(self):
        self.render("messageadmin.html")

class AgregarTarea(Handler):
    def get(self):
        self.render("agregartarea.html")
