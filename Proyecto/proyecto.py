import os
import webapp2
import jinja2
import logging
import httplib2
import datetime

from admin_controller.admin import *
from google.appengine.ext import ndb
from webapp2_extras import sessions

from google.appengine.api import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

from google.appengine.ext.webapp.mail_handlers import BounceNotification
from google.appengine.ext.webapp.mail_handlers import BounceNotificationHandler

from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator


global bandera
bandera= 0

def day(fecha):
    datelong= str(fecha)
    date= datelong[0:10]
    vector= date.split('-')
    return str(vector[2])

def month(fecha):
    meses =["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dec"]
    datelong= str(fecha)
    date= datelong[0:10]
    vector= date.split('-')
    num = vector[1]
    n=int(num)-1
    mes = meses[n]
    return str(mes)

def year(fecha):
    datelong= str(fecha)
    date= datelong[0:10]
    vector= date.split('-')
    return str(vector[0])

def hour(fecha):
    datelong= str(fecha)
    hour= datelong[11:19]
    return hour


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
jinja_env.filters['day'] = day
jinja_env.filters['month'] = month
jinja_env.filters['year'] = year
jinja_env.filters['hour'] = hour


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

#Describe las entidades del data Storex
class Cuentas(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.StringProperty()

class Correos(ndb.Model):
    mensaje_body = ndb.StringProperty()

class Login(Handler):
    def get(self):
        global bandera
        self.render("login.html",bandera=bandera)

    def post(self):
        global bandera
        user = self.request.get('lg_username')
        pw = self.request.get('lg_password')

        logging.info('Checking user='+ str(user) + 'pw='+ str(pw))
        msg = ''
        if pw == '' or user == '' :
            # msg = 'Please specify Account and Password'
            bandera = 1
            self.render("apphome.html", bandera=bandera)
        else:
            consulta=Cuentas.query(ndb.AND(Cuentas.username==user, Cuentas.password==pw )).get()
            if consulta is not None:
                logging.info('POST consulta=' + str(consulta))
                #Vinculo el usuario obtenido de mi datastore con mi sesion.
                bandera=0
                self.session['user'] = consulta.username
                logging.info("%s just logged in" % user)
                self.redirect('/')
            else:
                logging.info('POST consulta=' + str(consulta))
                bandera = 2
                # msg = 'Incorrect user or password.. please try again'
                self.render("apphome.html", bandera=bandera)

class Registro(Handler):
    def get(self):
        self.render("registro.html")

    def post(self):
        global bandera
        global mail_message
        to_email = self.request.get("reg_email")
        logging.info("message: " + message)
        bandera= 0
        user= self.request.get('reg_username')
        pw=self.request.get('reg_password')
        correo =self.request.get('reg_email')

        message = mail.EmailMessage(sender="Example.com Support <proyecto-eps@appspot.gserviceaccount.com>",
                                    subject="Your account has been approved")
        message.to = correo
        message.body = """
        Dear """+user+ """:
        Your example.com account has been approved.  You can now visit
        http://www.example.com/ and sign in using your Google Account to
        access new features.
        Please let us know if you have any questions.

        The toga Team
        """
        message.send()

        cuenta=Cuentas(username=user,password=pw,email=correo)
        cuentakey=cuenta.put()
        cuenta_user=cuentakey.get()

        if cuenta_user == cuenta:
            msg= "Gracias Por Registarse..."
            self.render("apphome.html",msg=msg,bandera=bandera)



class Index(Handler):
    def get(self):
        user = self.session.get('user')
        logging.info('Checkin index user value='+str(user))
        template_values={
            'user':user
            }
        self.render("index.html", user=template_values)

class AppHome(Handler):
   def get(self):
       global bandera
       bandera=0
       user = self.session.get('user')
       logging.info('Checkin index user value='+str(user))
       template_values={
           'user':user
           }
       self.render("apphome.html", user=template_values)

class Sitios(Handler):
   def get(self):
       user = self.session.get('user')
       logging.info('Checkin index user value='+str(user))
       template_values={
           'user':user
           }
       self.render("sitios.html", user=template_values)

class Logout(Handler):
    def get(self):
        if self.session.get('user'):
            msg = 'You are loging out..'
            self.render("logout.html", error=msg)
            del self.session['user']

class Message(Handler):
    def get(self):
        self.render("message.html")

class Profile(Handler):
    def get(self):
        self.render("profile.html")

class MailHandler(InboundMailHandler):
    def receive(self, mail_message):
        for content_type, pl in mail_message.bodies("text/plain"):
            mensaje = Correos(mensaje_body=pl.payload.decode('utf-8'))
            mensaje.put()

class LogBounceHandler(BounceNotificationHandler):
	def receive(self, bounce_message):
		logging.info('Received bounce post ... [%s]', self.request)
		logging.info('Bounce original: %s', bounce_message.original)
		logging.info('Bounce notification: %s', bounce_message.notification)

#************ oauth2Decorator
decorator = OAuth2Decorator(
    client_id='141147046388-jekjfmorkjlhpt5eh9nh9rvuk3h443lv.apps.googleusercontent.com',
    client_secret='foKPCKiZST5HloYvhGStc-iJ',
    scope='https://www.googleapis.com/auth/tasks https://www.googleapis.com/auth/calendar')
service = build('tasks','v1')
service_calendar = build('calendar', 'v3')

class OAuth(Handler):
    @decorator.oauth_required
    def get(self):
         tasks=service.tasks().list(tasklist='@default').execute(http=decorator.http())
         items = tasks.get('items', [])
         notas = ','.join([task.get('title','') for task in items])
         lista = notas.split(',')
         numero = len(lista)
         self.render("oauth.html", items=items,num=numero)

    @decorator.oauth_required
    def post(self):
        bandera = self.request.get("bandera")

        if ( bandera == "1"):
             task = {
              'title': 'New Task'
              }
             service.tasks().insert(tasklist='@default', body=task).execute(http=decorator.http())
        elif (bandera == "0"):
            task_id = self.request.get('task_id',allow_multiple = True)
            # service.tasks().delete(tasklist='@default',task='MTU1MTAxNzI3NzEzNDc3NTI5NTY6MDo0MDU0ODEwMg').execute(http=decorator.http())
            # service.tasks().delete(tasklist='@default',task=task_id).execute(http=decorator.http())
            for a in task_id:
                service.tasks().delete(tasklist='@default',task=a).execute(http=decorator.http())
        else:
             task_id = self.request.get('task_id')
             task = service.tasks().get(tasklist='@default', task=task_id).execute(http=decorator.http())
             task['title'] = 'modificado'
             service.tasks().update(tasklist='@default', task=task_id, body=task).execute(http=decorator.http())



        tasks=service.tasks().list(tasklist='@default').execute(http=decorator.http())
        items = tasks.get('items', [])
        notas = ','.join([task.get('title','') for task in items])
        lista = notas.split(',')
        numero = len(lista)
        self.render("oauth.html", items=items, bandera=bandera, num=numero)

class Calendario(Handler):
    @decorator.oauth_required
    def get(self):
        http=decorator.http()
        request=service_calendar.events().list(calendarId='primary')
        response_calendar=request.execute(http=http)
        events =  response_calendar['items']

        self.render("calendario.html",eventos=events)

    @decorator.oauth_required
    def post(self):
        http=decorator.http()
        bandera = self.request.get("bandera")

        if ( bandera == "1"):
            event = {
                'summary': 'Google I/O 2015',
                'location': '800 Howard St., San Francisco, CA 94103',
                'description': 'A chance to hear more about Google\'s developer products.',
                'start': {
                    'dateTime': '2015-11-28T09:00:00',
                    'timeZone': 'America/Mexico_City',
                },
                'end': {
                    'dateTime': '2015-11-28T10:00:00',
                    'timeZone': 'America/Mexico_City',
                },
            }
            request = service_calendar.events().insert(calendarId='primary', body=event)
            response_calendar=request.execute(http=http)
        elif (bandera == "0"):
            calendar_id = self.request.get('calendar_id',allow_multiple = True)

            for a in calendar_id:
                request=service_calendar.events().delete(calendarId='primary', eventId=a)
                response_calendar=request.execute(http=http)
        else:
             calendar_id = self.request.get('calendar_id')
             event=service_calendar.events().get(calendarId='primary', eventId=calendar_id).execute(http=http)

             event['summary'] = 'Appointment at Somewhere'
             updated_event = service_calendar.events().update(calendarId='primary', eventId=calendar_id , body=event).execute(http=http)

        request=service_calendar.events().list(calendarId='primary')
        response_calendar=request.execute(http=http)
        events =  response_calendar['items']
        self.render("calendario.html",eventos=events)


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'some-secret-key',
}


app = webapp2.WSGIApplication([('/', Index),
            			       ('/application',AppHome),
            			       ('/sitios',Sitios),
            			       ('/registro',Registro),
            			       ('/login',Login),
            			       ('/logout',Logout),
                               ('/message',Message ),
                               ('/profile', Profile),
                               ('/admin/messageadmin',Messageadmin),
                               ('_ah/mail/',MailHandler),
                               ('/admin', AdminHandler),
                               ('/admin/AgregarTarea', AgregarTarea),
                               ('/OAuth',OAuth),
                               ('/calendario',Calendario),
                               (LogBounceHandler.mapping()),
                               (MailHandler.mapping()),
                               (decorator.callback_path, decorator.callback_handler())
                              ],
                              debug=True, config=config)
