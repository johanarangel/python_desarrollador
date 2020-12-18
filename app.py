#!/usr/bin/env python
'''
Página principal [Proyecto Programador Python]
---------------------------
Autor: Johana Rangel
Version: 1.0

Descripcion:
Programa creado para validar los permisos de circulación provincial.
'''

__author__ = "Johana Rangel"
__email__ = "johanarang@hotmail.com"
__version__ = "1.0"

import traceback
import io
import sys
import os
import base64
import json
import sqlite3
from datetime import datetime, timedelta
import requests

import numpy as np
from flask import Flask, request, jsonify, render_template, Response, redirect, url_for, session
import matplotlib
matplotlib.use('Agg')   # Para multi-thread, non-interactive backend (avoid run in main loop)
import matplotlib.pyplot as plt
# Para convertir matplotlib a imagen y luego a datos binarios
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as mpimg
from matplotlib.ticker import MaxNLocator

import empresa_valida
from config import config


# Crear el server Flask
app = Flask(__name__)

# Clave que utilizaremos para encriptar los datos
app.secret_key = "flask_session_key_inventada"

# Obtener la path de ejecución actual del script
script_path = os.path.dirname(os.path.realpath(__file__))

# Obtener los parámetros del archivo de configuración
config_path_name = os.path.join(script_path, 'config.ini')
db = config('db', config_path_name)
server = config('server', config_path_name)

# Enviar los datos de config de la DB
empresa_valida.db = db

@app.route("/")
def index():
    try:
        #Endopoints disponibles
        result = "<h1>Bienvenido!!</h1>"
        result += "<h2>Endpoints disponibles:</h2>"
        result += "<h3>[GET] /reset --> borrar y crear la base de datos</h3>"
        result += "<h3>[GET] /menu.html --> HTML de bienvenida con las acciones a realizar</h3>"
        result += "<h3>[GET] /empresa.html --> muestra el HTML con el formulario de registro</h3>"
        result += "<h3>[POST] /procesar --> ingreso del registro en la base de datos</h3>"
        result += "<h3>[GET] /validar_datos.html --> muestra el HTML de consulta de código en la base de datos</h3>"
        result += "<h3>[POST] /consulta --> se muestran en una tabla los datos por código consultado</h3>"
        result += "<h3>[GET] /salida --> salida del programa</h3>"
        result += "<h3>[GET] /validaciones_empresa?limit=[]&offset=[] --> muestra los registros de la empresa en formato json</h3>"
        result += "<h3>[GET] /grafico_riesgo --> muestra gráfico respecto a cantidad de personas por riesgo</h3>"
        result += "<h3>[GET] /registrar --> enlace para registro de usuario</h3>"
        result += "<h3>[POST] /registrar --> se obtienen los datos del formulario y se guardan en una BD</h3>"
        result += "<h3>[POST] /ingresar --> se verifica nombre de usuario y clave para ingreso a validación de la empresa</h3>"
        result += "<h3>[GET] /logout --> Terminar la sesion</h3>"
        
        return(result)
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/reset")
def reset():
    try:
        # Borrar y crear la base de datos
        empresa_valida.create_schema()
        empresa_valida.esquema()
        empresa_valida.esquema_usuario()
        return render_template('reset.html')
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/menu.html")
def menu():
    try:
        #Entrada principal con las acciones a realizar.
        return render_template('menu.html')
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/empresa.html", methods= ['GET'])  #Colocar el nombre del archivo html para que funcionen los botones.
def registro_empresa():
    if request.method == 'GET':
        try:
            # Entrada a formulario de empresa por sesión.
            if session['password'] in session:
                return render_template('empresa.html')
            else:
                #Respuesta a través de un archico html en caso de no registrarse.
                return render_template('error_ingreso.html')
           
        except:
            return jsonify({'trace': traceback.format_exc()})


@app.route('/procesar', methods=['POST'])
def procesar():
    
    if request.method == 'POST':
        try:
            # Obtener del HTTP POST JSON de los datos registrados por la empresa
            codigo = str(request.form.get('codigo'))
            empresa= str(request.form.get('empresa')).upper()
            actividad = str(request.form.get('actividad')).upper()
            nombre = str(request.form.get('nombre')).upper()
            dni = str(request.form.get('dni'))
            edad = str(request.form.get('edad')) 
            fecha_permiso = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            riesgo = str(request.form.get('riesgo')).upper() 
 

            if(codigo is None or codigo.isdigit() is False or
                empresa is None or empresa.isdigit() is True or
                actividad is None or actividad.isdigit() is True or 
                nombre is None or nombre.isdigit() is True or
                riesgo is None or riesgo.isdigit() is True or
                edad is None or edad.isdigit() is False or
                dni is None or dni.isdigit() is False):
                # Datos ingresados incorrectos
                return render_template('error_ingreso.html')

            else:
                #Completando la BD con los datos del HTTP.
                empresa_valida.insert(int(codigo), empresa, actividad, nombre, int(edad), int(dni), fecha_permiso, riesgo)
                
                #Se arma diccionario para pasar al archivo html.
                datos = {"codigo":codigo, "empresa":empresa, "actividad":actividad, "nombre":nombre,
                        "edad":edad, "dni":dni, "fecha_permiso":fecha_permiso, "riesgo":riesgo}

                #Se informa a través de un archivo html en formato tabla los datos ingresados.        
                return render_template('procesado.html', datos=datos)

        except:
            return jsonify({'trace': traceback.format_exc()})

@app.route("/validar_datos.html", methods= ['GET'])
def validar_datos():
    try:
        #Llamado del archivo html para ingresar código de circulación para
        #verificación de los registros realizados por la empresa.
        return render_template('validar_datos.html')
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/consulta", methods= ['POST'])
def consulta():

    if request.method == 'POST':
        try:
            #Se obtiene los datos del formulario (el código de permiso)
            code = str(request.form.get('codigo'))
            
            #Del módulo empresa_valida se usa la función consulta, que busca los datos
            #que corresponden al código.
            datos = empresa_valida.consulta(code)
            
            #Acá se verifica si no hay datos con el código ingresado, devuelve un archivo
            #html con la información no encontrada.
            if datos == []:
                return render_template('sin_registros.html')

            else:
                #Se separa los datos para insertarlos en la BD de ingresado.   
                codigo = datos[0][0]
                empresa= datos[0][1]
                actividad = datos[0][2]
                nombre = datos[0][3]
                edad = datos[0][4]
                dni = datos[0][5]
                fecha_permiso = datos[0][6]
                riesgo = datos[0][7]                 

                #Se usa el módulo empresa_valida con la función fill y completar la tabla de la BD ingresado
                empresa_valida.fill(codigo, empresa, actividad, nombre, edad, dni, fecha_permiso, riesgo)  
                
                #Retorna un archivo consulta.html con los resultados obtenidos.
                return render_template('consulta.html', datos=datos)
            
        except:
            return jsonify({'trace': traceback.format_exc()})

@app.route("/salida.html", methods= ['GET'])
def salir():
    try:
        # Retorna un archivo html informando la salida del programa.
        return render_template('salida.html')
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/validaciones_empresa")
def pulsaciones_tabla():
    try:
        # Mostrar todos los registros en formato Json
        result = show()
        return (result)
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/grafico_riesgo", methods= ['GET'])
def grafico_registrados():
    
    try:
        #Del módulo empresa_valida se usa la función grafico que trae los 
        #datos riesgos y cantidad_personas para el gráfico.
        riesgos, cantidad_personas = empresa_valida.grafico()
        
        fig = plt.figure(figsize=(16, 9))
        fig.suptitle('"Cantidad de personas por riesgo"', fontsize=18)
        ax = fig.add_subplot()
    
        ax.bar(riesgos, cantidad_personas,  label='N° de riesgos', color='darkgreen')
        ax.set_facecolor('mintcream')
        ax.set_xlabel('Riesgos', fontsize=15)
        ax.set_ylabel('N° personas', fontsize=15)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True)) #para redondear los valores en el eje y
        ax.legend()
        ax.get_xaxis().set_visible(True)

        # Convertir ese grafico en una imagen para enviar por HTTP
        # y mostrar en el HTML
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        plt.close(fig)  # Cerramos la imagen para que no consuma memoria del sistema
        return Response(output.getvalue(), mimetype='image/png')
       
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/registrar", methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'GET':
        
        try:
            #Retorna el archivo html para login de usuario
            return render_template('login_prueba.html')
    
        except:
            return jsonify({'trace': traceback.format_exc()})
        
    if request.method == 'POST':  
          
        try:
            #Obtener del HTTP POST JSON el nombre,clave y correo en una BD.
            nombre = str(request.form.get('name'))
            clave= str(request.form.get('password'))
            correo = str(request.form.get('email'))
           
            if(nombre is None or nombre.isdigit() is True or clave.isdigit() is False):
                # Datos ingresados incorrectos
                return render_template('error_enter.html')
            
            empresa_valida.fill_usuario(correo, clave, nombre) #completa tabla de BD con usuarios

            #Registra la sesión
            session['name'] = nombre
            session['password'] = clave
           
            #Devuelve el html de login_prueba para ingresar el usuario y clave registrado.
            return render_template('login_prueba.html')

        except:
            return jsonify({'trace': traceback.format_exc()})         

@app.route("/ingresar", methods=['POST'])
def ingresar():
    #Acá se recibe el ingreso del usuario una vez tenido su usuario y clave.
    if request.method == 'POST':  
        try:           
            #Procedimiento para verificar si usuario y clave están guardados en session
            nombre_login = str(request.form.get('name_login'))
            clave_login= str(request.form.get('password_login'))

            #Si la clave y nombre de usuario ingresados por formulario son iguales a los guardados
            # en la sesión retorna el formulario a completar por la empresa. 
            if 'password' in session or session['password'] == clave_login and session['name'] == nombre_login:
                return render_template('empresa.html', nombre_login=nombre_login)
            else:
                #Informa en caso no esté registrado.
                return render_template('error_ingreso.html')
                
        except:
            return jsonify({'trace': traceback.format_exc()})

@app.route("/logout")
def logout():
    try:
        # Borrar y cerrar la sesion
        session.clear()
        return redirect(url_for('/ingresar'))
    except:
        return jsonify({'trace': traceback.format_exc()})


def show(show_type='json'):

    # Obtener de la query string los valores de limit y offset
    limit_str = str(request.args.get('limit'))
    offset_str = str(request.args.get('offset'))

    limit = 0
    offset = 0

    if(limit_str is not None) and (limit_str.isdigit()):
        limit = int(limit_str)

    if(offset_str is not None) and (offset_str.isdigit()):
        offset = int(offset_str)

    if show_type == 'json':
        data = empresa_valida.report(limit=limit, offset=offset, dict_format=True)
        return jsonify(data)


if __name__ == '__main__':
    print('Proyecto desarrollador python!')
    #Lanzar server
    app.run(host=server['host'],
            port=server['port'],
            debug=True)
    