#Seccion de Librerias
import webapp2
import os
import jinja2
import random
import logging

#   Estas son variables globales que se ocuparán para  la
#   aplicacación web

nombre    =  str
guessesTaken = int
respuesta = int

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


#   Clase principal que recibe como paramentro una Clase Handeler que permite
#   manejar las platinllas html
#   La funcion get(self) es lo primero que se ejecuta en la aplicación web y lo
#   que hace es rendirizar la pagina index.html
#   La funcion  post(self) lo que hace es mandarle paramentros  y renderizar la
#   pagina index2.html

class MainPage(Handler):
    def get(self):
        self.render("index.html")

    def post(self):
        global nombre
        nombre = self.request.get('nombre')
        logging.info('El nombre es =' + str(nombre))
        self.render("index2.html",nombre = nombre)


#   la clase juego es la encargada de llevar el control del juego
#   La funcion get obtiene la plantilla de juego.html y la renderiza,
#   también inicializa el contador del numero de intentos y genera un
#   número random para compararlo con la respuesta del usuario.
class Juego(Handler):
        def get(self):
            global nombre
            global guessesTaken
            global respuesta

            respuesta = random.randint(1,20)
            guessesTaken = 1

            self.render("juego.html", nombre= nombre)
        def post(self):

            global nombre
            global respuesta
            global guessesTaken

            stguess = self.request.get('numero')
            logging.info('El numero es =' + str(stguess))
            guess = int(stguess)
            if guess == respuesta:
                mensaje= "Buen Trabajo, "  + nombre + "!   Adivininaste mi numero en "+ str(guessesTaken) + ' intentos!'

            elif guess < 0:
                mensaje= "Hey mejor escribe un numero que sea mayor de 0"
            elif guess < respuesta:
                mensaje=nombre +" tu adivinanza es demasiado baja, llevas " +  str(guessesTaken) + " intentos!"
            else:
                mensaje=nombre +" tu adivinanza es demasiado alta , llevas "  + str(guessesTaken) + " intentos!"
            if (guessesTaken == 6):
                mensaje= "La respuesta era: " + str(respuesta)
            else:
                guessesTaken= guessesTaken +1
            self.render("juego.html",nombre=nombre,mensaje=mensaje,guessesTaken= guessesTaken)

# Aqui se asocian los action de las paginas html con las clases declaradas.
application = webapp2.WSGIApplication([('/', MainPage),
                                     ('/accion1_post',MainPage),
                                     ('/accion1_get',Juego),
                                     ('/play_post',Juego),
                                     ('/juego',Juego)
                                     ], debug=True)
