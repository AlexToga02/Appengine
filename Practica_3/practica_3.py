# -*- encoding: utf-8 -*-
import os
import webapp2
import jinja2
import logging

from google.appengine.ext import ndb
from webapp2_extras import sessions


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
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

#Describe las entidades del data Storex
class Cuentas(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.StringProperty()

class Login(Handler):
	def get(self):
		self.render("login.html")

	def post(self):
		user = self.request.get('lg_username')
		pw = self.request.get('lg_password')

		logging.info('Checking user='+ str(user) + 'pw='+ str(pw))
		msg = ''
		if pw == '' or user == '' :
			msg = 'Please specify Account and Password'
			self.render("login.html", error=msg)
		else:
			consulta=Cuentas.query(ndb.AND(Cuentas.username==user, Cuentas.password==pw )).get()
			if consulta is not None:
				logging.info('POST consulta=' + str(consulta))
				#Vinculo el usuario obtenido de mi datastore con mi sesion.
				self.session['user'] = consulta.username
				logging.info("%s just logged in" % user)
				self.redirect('/')
			else:
				logging.info('POST consulta=' + str(consulta))
				msg = 'Incorrect user or password.. please try again'
				self.render("login.html", error=msg)
                
class Registro(Handler):
    def get(self):
	       self.render("registro.html")

    def post(self):
        user= self.request.get('reg_username')
        pw=self.request.get('reg_password')

        cuenta=Cuentas(username=user,password=pw)
        cuentakey=cuenta.put()
        cuenta_user=cuentakey.get()

        if cuenta_user == cuenta:
            print "Cuenta de usuario: ",cuenta_user
            print
            msg= "Gracias Por Registarse..."
            self.render("registro.html",error=msg)

        query = Cuentas.query()
        for resultado in query:
            print "Resultado.username: ",resultado.username
            print "resultado: ",resultado



class Index(Handler):
    def get(self):
        user = self.session.get('user')
        logging.info('Checkin index user value='+str(user))
        template_values={
            'user':user
            }
        self.render("index.html", user=template_values)

class Topicos(Handler):
   def get(self):
       user = self.session.get('user')
       logging.info('Checkin index user value='+str(user))
       template_values={
           'user':user
           }
       self.render("topicos.html", user=template_values)

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



config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'some-secret-key',
}

app = webapp2.WSGIApplication([('/', Index),
            			       ('/topicos',Topicos),
            			       ('/sitios',Sitios),
            			       ('/topicos',Topicos),
            			       ('/registro',Registro),
            			       ('/login',Login),
            			       ('/logout',Logout)
                              ],
                              debug=True, config=config)
