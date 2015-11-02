# -*- encoding: utf-8 -*-
import os
import webapp2
import jinja2
import logging

from google.appengine.ext import ndb
from webapp2_extras import sessions
<<<<<<< HEAD
=======
from google.appengine.api import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
>>>>>>> Combinados

global bandera
mail_message = mail.EmailMessage()
bandera= 0

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

<<<<<<< HEAD
=======
class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)

>>>>>>> Combinados
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

# class MainHandler(Handler):
# 	def get(self):
# 		self.render("_base.html")
#
# 	def post(self):
# 		#Capturo los datos de la vista
# 		global mail_message
# 		sender_email = self.request.get("contacto_email")
# 		logging.info("sender_email: " + sender_email)
# 		message = self.request.get("contacto_body")
# 		logging.info("message: " + message)
#
# 		#Defino el correo de la aplicación, en donde se mandará el mensaje.
# 		app_mail = "proyecto-eps@myapp.appspotmail.com"
#
# 		#Envió el correo a la aplicación.
# 		mail_message.sender = sender_email
# 		mail_message.to = app_mail
# 		mail_message.subject = "Esto es una prueba"
# 		mail_message.body = message
# 		mail_message.send()
#
# 		#Muestro un mensaje de que su mensaje ha sido enviado
#
# 		self.response.write("Gracias, su mensaje se ha enviado.")

class MailHandler(InboundMailHandler):
    def receive(self, mail_message):
        for content_type, pl in mail_message.bodies("text/plain"):
            mensaje = Correos(mensaje_body=pl.payload.decode('utf-8'))
            mensaje.put()

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
        bandera= 0
        user= self.request.get('reg_username')
        pw=self.request.get('reg_password')

        cuenta=Cuentas(username=user,password=pw)
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

class Messageadmin(Handler):
    def get(self):
        self.render("messageadmin.html")

class Paginaadmin(Handler):
    def get(self):
        self.render("paginaadmin.html")

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
<<<<<<< HEAD
                               ('/message',Message ),
                               ('/profile', Profile),
                               ('/messageadmin',Messageadmin),
                               ('/Paginaadmin',Paginaadmin)
=======
                               ('_ah/mail/',MailHandler),
                               (MailHandler.mapping())
>>>>>>> Combinados
                              ],
                              debug=True, config=config)
