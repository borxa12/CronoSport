#!/usr/bin/env python
# -*- codging:utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import jinja2
import os
import datetime
import time

JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=["jinja2.ext.autoescape"],
        autoescape=True
    )

class Entrenamiento(ndb.Model):
    usuario = ndb.StringProperty(required=True)
    deporte = ndb.StringProperty(required=True)
    tiempo_cadena = ndb.StringProperty(required=True)
    t_horas = ndb.IntegerProperty(required=True)
    t_minutos = ndb.IntegerProperty(required=True)
    t_segundos = ndb.IntegerProperty(required=True)
    distancia = ndb.FloatProperty(required=True)
    vel_media = ndb.FloatProperty(required=True)
    tiempo_100m = ndb.StringProperty(required=True)
    tiempo_1km = ndb.StringProperty(required=True)
    notas = ndb.TextProperty(required=False)
    fecha = ndb.DateProperty(auto_now_add=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect("/crono_sport")
            return
        else:
            access_link = users.create_login_url("/crono_sport")
        template_values = {'access_link': access_link}
        template = JINJA_ENVIRONMENT.get_template("index.html")
        self.response.write(template.render(template_values))

class CronoSportHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            user_name = user.nickname()
            access_link = users.create_logout_url("/")
            entrenamientos = Entrenamiento.query(Entrenamiento.usuario == user.user_id()).order(-Entrenamiento.fecha)
            template_values = {
                'user_name': user_name,
                'access_link': access_link,
                'entrenamientos': entrenamientos
            }
            template = JINJA_ENVIRONMENT.get_template("crono_sport.html")
            self.response.write(template.render(template_values))
        else:
            self.redirect("/")

class AddEntrenamientoHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            user_name = user.nickname()
            access_link = users.create_logout_url("/")
            template_values = {'user_name': user_name,
                'access_link': access_link
            }
            template = JINJA_ENVIRONMENT.get_template("add.html")
            self.response.write(template.render(template_values))
        else:
            self.redirect("/")

    def post(self):
        inputFecha = ""
        inputDeporte = ""
        inputTiempoHoras = ""
        inputTiempoMinutos = ""
        inputTiempoSegundos = ""
        inputDistancia = ""
        inputNotas = ""
        inputKey = ""
        action = ""
        try:
            inputFecha = self.request.get("inputFecha")
            inputDeporte = self.request.get("inputDeporte")
            inputTiempoHoras = self.request.get("inputTiempoHoras")
            inputTiempoMinutos = self.request.get("inputTiempoMinutos")
            inputTiempoSegundos = self.request.get("inputTiempoSegundos")
            inputDistancia = self.request.get("inputDistancia")
            inputNotas = self.request.get("inputNotas")

            # Calculo de la Fecha
            f = inputFecha + " 00:00:00"
            date = datetime.datetime.strptime(f,"%Y-%m-%d %H:%M:%S")

            # Calculo del Deporte
            if(int(inputDeporte) == 1):
                d = "Correr"
            elif (int(inputDeporte) == 2):
                d = "Natacion"
            elif (int(inputDeporte) == 3):
                d = "Ciclismo"

            # Pasar tiempo a segundos
            t = int(inputTiempoHoras) * 3600 + int(inputTiempoMinutos) * 60 + int(inputTiempoSegundos)

            # Convertir Tiempo a Cadena (h:mm:ss)
            t_string = tiempoToString(int(inputTiempoHoras),int(inputTiempoMinutos),int(inputTiempoSegundos))

            # Calculo de la Velocidad Media
            v_media = velocidadMedia(inputDistancia,t)

            # Calculo del tiempo para realizar 100 metros
            t100m_horas, t100m_minutos, t100m_segundos = t100m(inputDistancia,t)
            t100m_string = tiempoToString(t100m_horas,t100m_minutos,t100m_segundos)

            # Calculo del tiempo para realizar 1 kilometro
            t1k_horas,t1k_minutos,t1k_segundos = t1k(inputDistancia,t)
            t1k_string = tiempoToString(int(t1k_horas),int(t1k_minutos),int(t1k_segundos))

            # Insertar Entrenamiento
            user = users.get_current_user()
            entrenamiento = Entrenamiento(usuario = user.user_id(), deporte = d,
                tiempo_cadena = t_string, t_horas = int(inputTiempoHoras),
                t_minutos = int(inputTiempoMinutos), t_segundos = int(inputTiempoSegundos),
                distancia = float(inputDistancia), vel_media = float(v_media),
                tiempo_100m = t100m_string, tiempo_1km = t1k_string,
                notas = inputNotas, fecha = date)
            entrenamiento.put()
            time.sleep(1)
            self.redirect("/")
        except:
            self.redirect("/error")

class ModifyEntrenamientoHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            user_name = user.nickname()
            access_link = users.create_logout_url("/")
            entrenamiento_key = self.request.GET['id']
            entrenamiento = ndb.Key(urlsafe = entrenamiento_key).get()
            template_values = {'user_name': user_name,
                'access_link': access_link,
                'entrenamiento': entrenamiento
            }
            template = JINJA_ENVIRONMENT.get_template("modify.html")
            self.response.write(template.render(template_values))
        else:
            self.redirect("/")

    def post(self):
        inputFecha = ""
        inputDeporte = ""
        inputTiempoHoras = ""
        inputTiempoMinutos = ""
        inputTiempoSegundos = ""
        inputDistancia = ""
        inputNotas = ""
        inputKey = ""
        action = ""
        try:
            inputFecha = self.request.get("inputFecha")
            inputDeporte = self.request.get("inputDeporte")
            inputTiempoHoras = self.request.get("inputTiempoHoras")
            inputTiempoMinutos = self.request.get("inputTiempoMinutos")
            inputTiempoSegundos = self.request.get("inputTiempoSegundos")
            inputDistancia = self.request.get("inputDistancia")
            inputNotas = self.request.get("inputNotas")

            # Calculo de la Fecha
            f = inputFecha + " 00:00:00"
            date = datetime.datetime.strptime(f,"%Y-%m-%d %H:%M:%S")

            # Calculo del Deporte
            if(int(inputDeporte) == 1):
                d = "Correr"
            elif (int(inputDeporte) == 2):
                d = "Natacion"
            elif (int(inputDeporte) == 3):
                d = "Ciclismo"

            # Pasar tiempo a segundos
            t = int(inputTiempoHoras) * 3600 + int(inputTiempoMinutos) * 60 + int(inputTiempoSegundos)

            # Convertir Tiempo a Cadena (h:mm:ss)
            t_string = tiempoToString(int(inputTiempoHoras),int(inputTiempoMinutos),int(inputTiempoSegundos))

            # Calculo de la Velocidad Media
            v_media = velocidadMedia(inputDistancia,t)

            # Calculo del tiempo para realizar 100 metros
            t100m_horas, t100m_minutos, t100m_segundos = t100m(inputDistancia,t)
            t100m_string = tiempoToString(t100m_horas,t100m_minutos,t100m_segundos)

            # Calculo del tiempo para realizar 1 kilometro
            t1k_horas,t1k_minutos,t1k_segundos = t1k(inputDistancia,t)
            t1k_string = tiempoToString(int(t1k_horas),int(t1k_minutos),int(t1k_segundos))

            # Insertar Entrenamiento
            entrenamiento_key = self.request.GET['id']
            entrenamiento = ndb.Key(urlsafe = entrenamiento_key).get()
            entrenamiento.deporte = d
            entrenamiento.tiempo_cadena = t_string
            entrenamiento.t_horas = int(inputTiempoHoras)
            entrenamiento.t_minutos = int(inputTiempoMinutos)
            entrenamiento.t_segundos = int(inputTiempoSegundos)
            entrenamiento.distancia = float(inputDistancia)
            entrenamiento.vel_media = float(v_media)
            entrenamiento.tiempo_100m = t100m_string
            entrenamiento.tiempo_1km = t1k_string
            entrenamiento.notas = inputNotas
            entrenamiento.fecha = date
            entrenamiento.put()
            time.sleep(1)
            self.redirect("/")
        except:
            self.redirect("/error")

class DeleteHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            user_name = user.nickname()
            access_link = users.create_logout_url("/")
            try:
                entrenamiento_key = self.request.GET['id']
                ndb.Key(urlsafe = entrenamiento_key).delete()
                time.sleep(1)
                self.redirect("/")
            except:
                self.redirect("/error")
        else:
            self.redirect("/")

class ErrorHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        access_main = "/"
        if user:
            user_name = user.nickname()
            template_values = {'user_name': user_name,
                'access_main': access_main
            }
            template = JINJA_ENVIRONMENT.get_template("error.html")
            self.response.write(template.render(template_values))
        else:
            self.redirect("/")

# Calcula la Velocidad Media. Devuelve un float con dos decimales
def velocidadMedia(distancia,t):
    vm = float(distancia) / (int(t)/3600.0)
    return round(vm,2)

# Calcula el tiempo en recorrer 100 m. Devuelve tres enteros correspondientes a las horas, minutos y segundos
def t100m(distancia,t):
    t100m = t / (float(distancia) * 10.0)
    segundos = t100m%60
    min_aux = t100m//60
    minutos = min_aux%60
    horas = min_aux//60
    return int(horas), int(minutos), int(segundos)

# Calcula el tiempo en recorrer 1 km. Devuelve tres enteros correspondientes a las horas, minutos y segundos
def t1k(distancia,t):
    t1k = int(t) / float(distancia)
    segundos = t1k%60
    min_aux = t1k//60
    minutos = min_aux%60
    horas = min_aux//60
    return int(horas), int(minutos), int(segundos)

# Convierte tres numero entores a un string tal que: H horas  MM min  SS seg
def tiempoToString(horas,minutos,segundos):
    string = ""
    if int(horas) == 0:
        if int(minutos) == 0:
            if int(segundos) < 10:
                seg_string = "0" + str(segundos)
            else:
                seg_string = str(segundos)
            string = seg_string + " seg"
        else:
            min_string = str(minutos)
            if int(segundos) < 10:
                seg_string = "0" + str(segundos)
            else:
                seg_string = str(segundos)
            string = min_string + " min  " + seg_string + " seg"
    else:
        horas_string = str(horas)
        if int(minutos) < 10:
            min_string = "0" + str(minutos)
        else:
            min_string = str(minutos)
        if int(segundos) < 10:
            seg_string = "0" + str(segundos)
        else:
            seg_string = str(segundos)
        string = horas_string + " horas  " + min_string + " min  " + seg_string + " seg"
    return string

# Extrae los nUmero de un String de tiempo (H horas  MM min  SS seg). Devuelve las horas, minutos y segundos
# Sin usar de momento
# def tiempoToInt(tiempoString):
#     tiempo_fragmentado = tiempoString.split("  ")
#     if len(tiempo_fragmentado) == 1:
#         horas = 0
#         minutos = 0
#         for i in range(len(tiempo_fragmentado)):
#             if i == 0:
#                 segundos = tiempo_fragmentado[i].split(" ")[0]
#     elif  len(tiempo_fragmentado) == 2:
#         for i in range(len(tiempo_fragmentado)):
#             horas = 0
#             if i == 0:
#                 minutos = tiempo_fragmentado[i].split(" ")[0]
#             elif i == 1:
#                 segundos = tiempo_fragmentado[i].split(" ")[0]
#     elif  len(tiempo_fragmentado) == 3:
#         for i in range(len(tiempo_fragmentado)):
#             if i == 0:
#                 horas = tiempo_fragmentado[i].split(" ")[0]
#             elif i == 1:
#                 minutos = tiempo_fragmentado[i].split(" ")[0]
#             elif i == 2:
#                 segundos = tiempo_fragmentado[i].split(" ")[0]
#     return horas, minutos, segundos


app = webapp2.WSGIApplication([
            ('/', MainHandler),
            ('/crono_sport', CronoSportHandler),
            ('/add', AddEntrenamientoHandler),
            ('/modify', ModifyEntrenamientoHandler),
            ('/delete', DeleteHandler),
            ('/error', ErrorHandler)
        ], debug=True
    )
