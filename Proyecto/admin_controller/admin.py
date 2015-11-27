import webapp2
import os
import jinja2

from webapp2_extras import sessions
from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator
from Crypto.Hash import SHA256
from google.appengine.ext import ndb

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

template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')


jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
jinja_env.filters['day'] = day
jinja_env.filters['month'] = month
jinja_env.filters['year'] = year
jinja_env.filters['hour'] = hour
jinja_env.filters['date'] = date
jinja_env.filters['time'] = time

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

def check_password(clear_password, password_hash):
    return SHA256.new(clear_password).hexdigest() == password_hash

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


class Tareas(Handler):
    @decorator.oauth_required
    def get(self):
         tasks=service.tasks().list(tasklist='@default').execute(http=decorator.http())
         items = tasks.get('items', [])
         notas = ','.join([task.get('title','') for task in items])
         lista = notas.split(',')
         numero = len(lista)
         self.render("tareas.html", items=items,num=numero)

    @decorator.oauth_required
    def post(self):
        bandera = self.request.get("bandera")

        if ( bandera == "1"):
            title=self.request.get("title")
            task = {
                'title': title
            }
            service.tasks().insert(tasklist='@default', body=task).execute(http=decorator.http())
        elif (bandera == "0"):
            task_id = self.request.get('task_id',allow_multiple = True)
            # service.tasks().delete(tasklist='@default',task='MTU1MTAxNzI3NzEzNDc3NTI5NTY6MDo0MDU0ODEwMg').execute(http=decorator.http())
            # service.tasks().delete(tasklist='@default',task=task_id).execute(http=decorator.http())
            for a in task_id:
                service.tasks().delete(tasklist='@default',task=a).execute(http=decorator.http())
        elif (bandera=="2"):
             task_id = self.request.get('task_id')
             task = service.tasks().get(tasklist='@default', task=task_id).execute(http=decorator.http())
             task['title'] = 'modificado'
             service.tasks().update(tasklist='@default', task=task_id, body=task).execute(http=decorator.http())



        tasks=service.tasks().list(tasklist='@default').execute(http=decorator.http())
        items = tasks.get('items', [])
        notas = ','.join([task.get('title','') for task in items])
        lista = notas.split(',')
        numero = len(lista)

        http=decorator.http()
        request=service_calendar.events().list(calendarId='primary')
        response_calendar=request.execute(http=http)
        events =  response_calendar['items']

        self.render("paginaadmin.html",eventos=events,bandera=bandera,items=items,num=numero)


class Calendario(Handler):
    @decorator.oauth_required
    def get(self):

        http=decorator.http()
        # request=service_calendar.events().list(calendarId='primary')
        # response_calendar=request.execute(http=http)
        # events =  response_calendar['items']
        calendar_id = self.request.get('calendar_id')
        event=service_calendar.events().get(calendarId='primary', eventId=calendar_id).execute(http=http)

        self.render("eventoupdate.html",evento=event)

    @decorator.oauth_required
    def post(self):
        http=decorator.http()
        bandera = self.request.get("bandera")

        if ( bandera == "1"):
            summary=self.request.get("eventName")
            location=self.request.get("lugar")
            description = self.request.get("descripcion")
            fechaini=self.request.get("fechaini")
            hora=self.request.get("horaini")
            datetimeS=fechaini+'T'+hora
            fechafin=self.request.get("fechafin")
            horaf=self.request.get("horafin")
            datetimeE=fechafin+'T'+horaf


            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': datetimeS,
                    'timeZone': 'America/Mexico_City',
                },
                'end': {
                    'dateTime': datetimeE,
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
        elif  (bandera == "2"):
             event_id = self.request.get('calendar_id')
             summary = self.request.get("summary")
             description=self.request.get("description")
             location= self.request.get("location")
             fechaini=self.request.get("fechaini")
             fechafin=self.request.get("fechafin")
             horaini=self.request.get("horaini")
             horafin=self.request.get("horafin")
             datetimeS=fechaini+'T'+horaini
             datetimeE=fechafin+'T'+horafin
             event = service_calendar.events().get(calendarId='primary', eventId=event_id ).execute(http=http)

             event = {
                 'summary': summary,
                 'location': location,
                 'description': description,
                 'start': {
                     'dateTime': datetimeS,
                     'timeZone': 'America/Mexico_City',
                 },
                 'end': {
                     'dateTime': datetimeE,
                     'timeZone': 'America/Mexico_City',
                 },
             }

             updated_event = service_calendar.events().update(calendarId='primary', eventId=event_id , body=event).execute(http=http)

        request=service_calendar.events().list(calendarId='primary')
        response_calendar=request.execute(http=http)
        events =  response_calendar['items']
        self.render("paginaadmin.html",eventos=events)



class Messageadmin(Handler):
    def get(self):
        self.render("messageadmin.html")

class Eventos(Handler):
    def get(self):
        self.render("agregarevento.html")

class VerEvento(Handler):
    def get(self):
        self.render("verevento.html")

class Domicilioo(ndb.Model):
    calle = ndb.StringProperty()
    num_int = ndb.StringProperty()
    num_ext = ndb.IntegerProperty()
    colonia = ndb.StringProperty()
    ciudad = ndb.StringProperty()
    pais = ndb.StringProperty()
    codpos = ndb.IntegerProperty()

class Factura(ndb.Model):
    nomempresa = ndb.StringProperty(required=True)
    domicilio = ndb.StructuredProperty(Domicilioo,repeated=True)
    correo = ndb.StringProperty(required=True)
    rfc = ndb.StringProperty(required=True)

class Facturas(Handler):
    def get(self):
        consulta= Factura.query().fetch()
        self.render("facturas.html", facturas=consulta)
