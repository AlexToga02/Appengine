import webapp2
import os
import jinja2

from webapp2_extras import sessions
from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator

template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')


jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

#************ oauth2Decorator
decorator = OAuth2Decorator(
    client_id='141147046388-jekjfmorkjlhpt5eh9nh9rvuk3h443lv.apps.googleusercontent.com',
    client_secret='foKPCKiZST5HloYvhGStc-iJ',
    scope='https://www.googleapis.com/auth/tasks https://www.googleapis.com/auth/calendar')
service = build('tasks','v1')
service_calendar = build('calendar', 'v3')

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
    @decorator.oauth_required
    def get(self):
         tasks=service.tasks().list(tasklist='@default').execute(http=decorator.http())
         items = tasks.get('items', [])
         notas = ','.join([task.get('title','') for task in items])
         lista = notas.split(',')
         numero = len(lista)

        http=decorator.http()
        request=service_calendar.events().list(calendarId='primary')
        response_calendar=request.execute(http=http)
        events =  response_calendar['items']

        self.render("paginaadmin.html",eventos=events,items=items,num=numero)

class Messageadmin(Handler):
    def get(self):
        self.render("messageadmin.html")

class AgregarTarea(Handler):
    def get(self):
        self.render("agregartarea.html")
