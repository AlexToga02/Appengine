# -*- encoding: utf-8 -*-
import os
import webapp2
import jinja2
import logging
import random
import urllib

from google.appengine.ext import ndb
from webapp2_extras import sessions


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

winned= 0
lost = 0
guesses = ""
guess = ""
secret = ""
turns = 0
missed= 0
missed2=0
msg=""
letters = ['b', 'c', 'd','f', 'g', 'h',
        'j', 'k', 'l', 'm', 'n','p', 'q', 'r', 's',
        't','v', 'w', 'x', 'y', 'z']
desactivar=[]
animal=[]

img=""


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
    fullname = ndb.StringProperty()
    Address   = ndb.StringProperty()
    gender   = ndb.StringProperty()
    wins     = ndb.IntegerProperty(default=0)
    losses     = ndb.IntegerProperty(default=0)

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
        fullname=self.request.get('reg_fullname')
        address=self.request.get('reg_address')
        gender=self.request.get('reg_gender')

        cuenta=Cuentas(username=user,password=pw,fullname=fullname,Address=address,gender=gender)
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

class Jugar(Handler):
   def get(self):
       global secret
       global guesses
       global turns
       global missed
       global msg
       global desactivar
       global animal
       global img

       user = self.session.get('user')
       logging.info('Checkin index user value='+str(user))
       animals = urllib.urlopen('http://davidbau.com/data/animals').read().split()
       desactivar=[]
       animal=[]
       missed=0


       turns = 5
       msg=""
       guesses = 'aeiou'
       secret = random.choice(animals)



       for le in secret:
            if le not in guesses:
                animal.append('_')
                missed +=1
            else:
                 animal.append(le)

       template_values={
           'user':user
           }
       img="img/hangman0.jpg"

       self.render("juego.html", img=img,user=template_values,letters=letters,animal=animal,secret=secret,turns=turns,missed=missed)

   def post(self):
       global turns
       global guess
       global guesses
       global secret
       global missed
       global msg
       global letters
       global desactivar
       global winned
       global lost
       global img

       missed = 0
       msg=""
       user = self.session.get('user')
       letra= self.request.get('letra')
       letra=str(letra)
       desactivar.append(letra)
       guesses += letra
       index=0

       for le in secret:
            if le not in guesses:
                missed +=1
            else:
                 animal[index]=le
            index+=1

       if missed == 0:
            msg="Ganasteeeee!!!"
            desactivar=letters
            winned += 1
            query = Cuentas.query(Cuentas.username == user).get()
            if query is not None:
                query.wins += 1
                query.put()
            # if consulta is not None:
            #     consulta.winned = wined
            #     consulta.put()

       if letra not in secret:
           turns -=1
           msg = "No es la letra correcta."
           if turns < 5: img="img/hangman1.jpg"
           if turns < 4: img="img/hangman2.jpg"
           if turns < 3: img="img/hangman3.jpg"
           if turns < 2: img="img/hangman4.jpg"
           if turns < 1: img="img/hangman5.jpg"
           if turns == 0:
               msg='La respuesta correcta es..'+str(secret)
               desactivar=letters
               lost += 1
               query = Cuentas.query(Cuentas.username == user).get()
               if query is not None:
                   query.losses += 1
                   query.put()
            #    if consulta is not None:
            #        consulta.losses = lost
            #        consulta.put()



       template_values={
           'user':user
        }
       self.render("juego.html", img=img,animal=animal,missed=missed,desac=desactivar,user=template_values,letters=letters,  secret=secret,letra=letra,guesses=guesses,msg=msg,turns=turns)

class Sitios(Handler):
   def get(self):
       user = self.session.get('user')
       logging.info('Checkin index user value='+str(user))
       template_values={
           'user':user
           }
       self.render("sitios.html", user=template_values)


class Profile(Handler):
   def get(self):
       user = self.session.get('user')
       query = Cuentas.query(Cuentas.username == user).get()
       print query
       logging.info('Checkin index user value='+str(user))
       template_values={
           'user':user
           }
       self.render("perfil.html", user=template_values,usuario=query)


class Logout(Handler):
    def get(self):
        if self.session.get('user'):
            msg = 'You are loging out..'
            self.render("logout.html", error=msg)
            del self.session['user']
            self.redirect('/')



config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'some-secret-key',
}

app = webapp2.WSGIApplication([('/', Index),
            			       ('/juego',Jugar),
            			       ('/registro',Registro),
                               ('/sitios',Sitios    ),
            			       ('/login',Login),
            			       ('/logout',Logout),
                               ('/perfil',Profile)
                              ],
                              debug=True, config=config)
