import os
import webapp2
import jinja2
import logging
import httplib2


from Crypto.Hash import SHA256
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
    hour= datelong[11:16]
    return hour

def date(fecha):
    datelong= str(fecha)
    hour= datelong[0:10]
    return hour

def time(fecha):
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
jinja_env.filters['date'] = date
jinja_env.filters['time'] = time

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def check_password(clear_password, password_hash):
    return SHA256.new(clear_password).hexdigest() == password_hash

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
    email   =  ndb.StringProperty()


class Domicilioo(ndb.Model):
    calle = ndb.StringProperty()
    num_int = ndb.StringProperty()
    num_ext = ndb.IntegerProperty()
    colonia = ndb.StringProperty()
    ciudad = ndb.StringProperty()
    pais = ndb.StringProperty()
    codpos = ndb.IntegerProperty()

class NombreCompleto(ndb.Model):
    nombres= ndb.StringProperty()
    apellidos= ndb.StringProperty()

class Usuario(ndb.Model):
    nomcompleto = ndb.StructuredProperty(NombreCompleto, repeated=True)
    domicilio = ndb.StructuredProperty(Domicilioo,repeated=True)
    profesion = ndb.StringProperty()
    puesto = ndb.StringProperty()
    cuenta = ndb.StructuredProperty(Cuentas,repeated=True)
    perfilupdated= ndb.BooleanProperty(default=False)

class Factura(ndb.Model):
    nomempresa = ndb.StringProperty(required=True)
    domicilio = ndb.StructuredProperty(Domicilioo,repeated=True)
    correo = ndb.StringProperty(required=True)
    rfc = ndb.StringProperty(required=True)


class Evento(ndb.Model):
    nomevento = ndb.StringProperty()
    descripcion = ndb.StringProperty()
    datet = ndb.StringProperty()
    lugar = ndb.StringProperty()
    cupo = ndb.IntegerProperty()


class Correos(ndb.Model):
    mensaje_body = ndb.StringProperty()

class Login(Handler):
    def get(self):
        global bandera
        self.render("login.html",bandera=bandera)

    def post(self):
        global bandera
        user = self.request.get('lg_username')
        pw=SHA256.new(self.request.get('lg_password')).hexdigest()

        logging.info('Checking user='+ str(user) + 'pw='+ str(pw))
        msg = ''
        if pw == '' or user == '' :
            # msg = 'Please specify Account and Password'
            bandera = 1
            self.render("apphome.html", bandera=bandera)
        else:
            consulta=Usuario.query(ndb.AND(Usuario.cuenta.username==user,Usuario.cuenta.password==pw)).get()

            if consulta is not None:
                logging.info('POST consulta=' + str(consulta))
                #Vinculo el usuario obtenido de mi datastore con mi sesion.
                bandera=0
                self.session['user'] =consulta.cuenta[0].username
                logging.info("%s just logged in" % user)
                if consulta.perfilupdated:
                    self.redirect('/entradausuario')
                else:
                    self.redirect('/perfil')
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
        pw=SHA256.new(self.request.get('reg_password')).hexdigest()
        email=self.request.get('reg_email')
        nombres=self.request.get('reg_firstname')
        apellidos=self.request.get('reg_lastname')

        usuario=Usuario(cuenta=[Cuentas(username= user,password=pw,email=email)],
                        nomcompleto=[NombreCompleto(nombres=nombres,apellidos=apellidos)],
                        domicilio=[Domicilioo(calle=" ")])
        userkey=usuario.put()
        cuenta_user=userkey.get()

        if cuenta_user == usuario:
            msg= "Gracias Por Registarse..."
            self.render("apphome.html",msg=msg,bandera=bandera)


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
       if self.session.get('user'):
           self.redirect("/admin")
       else:
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

class EntradaUsuario(Handler):
    def get(self):
        consulta=Evento.query().fetch()
        self.render("entradausuario.html",eventos=consulta)

class DFactura(Handler):
    def get(self):

        self.render("dfacturacion.html")

    def post(self):
        nomempresa= self.request.get('nomempresa')
        correo=self.request.get('correo')
        rfc=self.request.get('rfc')
        pais=self.request.get('pais')
        ciudad=self.request.get('ciudad')
        calle= self.request.get('calle')
        colonia=self.request.get('colonia')
        num_int=self.request.get('numint')
        num_ext=int(self.request.get('numext'))
        codpos=int(self.request.get('codpos'))

        facturas=Factura(nomempresa=nomempresa,
                        rfc=rfc,
                        correo=correo,
                        domicilio=[Domicilioo(pais=pais,
                                              ciudad=ciudad,
                                              calle=calle,
                                              colonia=colonia,
                                              num_ext=num_ext,
                                              num_int=num_int,
                                              codpos=codpos)])
        facturaskey=facturas.put()
        cuenta_factura=facturaskey.get()

        if cuenta_factura == facturas:
            msg= "Datos Guardados Correctamente"
            self.render("dfacturacion.html",msg=msg)
class Profile(Handler):
    def get(self):
        if self.session.get('user'):
            user = self.session.get('user')
            consulta=Usuario.query(Usuario.cuenta.username==user).get()
            self.render("profile.html", query=consulta,  user=user)

    def post(self):
        nombres= self.request.get('nombres')
        apellidos = self.request.get('apellidos')
        correo = self.request.get('correo')
        profesion= self.request.get('profesion')
        puesto = self.request.get('puesto')
        calle = self.request.get('calle')
        num_int = self.request.get('numint')
        num_ext = int(self.request.get('numext'))
        colonia = self.request.get('colonia')
        ciudad = self.request.get('ciudad')
        pais = self.request.get('pais')
        codpos = int(self.request.get('codpos'))
        user = self.session.get('user')
        consulta=Usuario.query(Usuario.cuenta.username==user).get()

        if consulta is not None:

            consulta.nomcompleto[0].nombres = nombres
            consulta.nomcompleto[0].apellidos = apellidos
            consulta.cuenta[0].email = correo
            consulta.profesion = profesion
            consulta.puesto = puesto
            consulta.domicilio[0].pais = pais
            consulta.domicilio[0].ciudad = ciudad
            consulta.domicilio[0].colonia = colonia
            consulta.domicilio[0].calle = calle
            consulta.domicilio[0].codpos = codpos
            consulta.domicilio[0].num_int = num_int
            consulta.domicilio[0].num_ext = num_ext
            consulta.perfilupdated=True
            consulta.put()
        msg="Perfil Actualizado"
        self.render("profile.html",  query=consulta, msg=msg)



#************ oauth2Decorator
decorator = OAuth2Decorator(
    client_id='141147046388-jekjfmorkjlhpt5eh9nh9rvuk3h443lv.apps.googleusercontent.com',
    client_secret='foKPCKiZST5HloYvhGStc-iJ',
    scope='https://www.googleapis.com/auth/tasks https://www.googleapis.com/auth/calendar')
service = build('tasks','v1')
service_calendar = build('calendar', 'v3')




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
                               ('/perfil', Profile),
                               ('/admin/messageadmin',Messageadmin),
                               ('/admin', AdminHandler),
                               ('/admin/tareas',Tareas),
                               ('/admin/calendario',Calendario),
                               ('/admin/evento',Eventos),
                               ('/admin/VerEvento', VerEvento),
                               ('/entradausuario',EntradaUsuario),
                               ('/dfacturacion',DFactura),
                               ('/admin/facturas', Facturas),
                               (MailHandler.mapping()),
                               (LogBounceHandler.mapping()),
                               (decorator.callback_path, decorator.callback_handler())
                              ],
                              debug=True, config=config)
