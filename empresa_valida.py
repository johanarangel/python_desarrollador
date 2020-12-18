#!/usr/bin/env python
'''
Módulo empresa_valida con funciones usadas en la app.py
---------------------------
Autor: Johana Rangel
Version: 1.0

Descripcion:
Programa creado para administrar la base de datos de registro
de empleados validados por la empresa, de usuarios e ingresados.
También de búsqueda de información en las BD.
'''

__author__ = "Johana Rangel"
__email__ = "johanarang@hotmail.com"
__version__ = "1.0"

import os
import sqlite3
import requests
import json

db = {}


def create_schema():

    # Conectarnos a la base de datos
    # En caso de que no exista el archivo se genera
    # como una base de datos vacia
    conn = sqlite3.connect(db['database'])

    # Crear el cursor para poder ejecutar las querys
    c = conn.cursor()

    # Obtener el path real del archivo de schema
    script_path = os.path.dirname(os.path.realpath(__file__))
    schema_path_name = os.path.join(script_path, db['schema'])

    # Crar esquema desde archivo
    c.executescript(open(schema_path_name, "r").read())

    # Para salvar los cambios realizados en la DB debemos
    # ejecutar el commit, NO olvidarse de este paso!
    conn.commit()

    # Cerrar la conexión con la base de datos
    conn.close()

def insert(codigo, empresa, actividad, nombre, edad, dni, fecha_permiso, riesgo):
    
    #Conecta con la BD
    conn = sqlite3.connect(db['database'])
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()

    values = [codigo, empresa, actividad, nombre, edad, dni, fecha_permiso, riesgo]
    
    try: 
        c.execute("""
            INSERT INTO validacion (codigo, empresa, actividad, nombre, edad, dni, fecha_permiso, riesgo)
            VALUES (?,?,?,?,?,?,?,?);""", values)

    except sqlite3.IntegrityError:
        return print('...')

    conn.commit()
    # Cerrar la conexión con la base de datos
    conn.close()

def consulta(codigo):
    
    #Conecta con la BD
    conn = sqlite3.connect(db['database'])
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()

    c.execute("""SELECT codigo, empresa, actividad, nombre, edad, dni, fecha_permiso, riesgo
                FROM validacion 
                WHERE codigo = ?;""", (codigo,))
    
    query_results = c.fetchall()

    conn.commit()
    # Cerrar la conexión con la base de datos
    conn.close()

    #Retorna los resultados obtenidos.
    return query_results

def grafico():

    #Conecta con la BD
    conn = sqlite3.connect(db['database'])
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()

    c.execute("""SELECT riesgo, COUNT(dni) as cantidad_personas FROM validacion GROUP BY riesgo;""")
    
    query_results = c.fetchall()

    conn.commit()
    # Cerrar la conexión con la base de datos
    conn.close()

    riesgos= [x[0] for x in query_results]
    cantidad_personas = [x[1] for x in query_results]

    #Retorna los resultados obtenidos
    return riesgos, cantidad_personas

def esquema():

    # Conectarnos a la base de datos
    # En caso de que no exista el archivo se genera
    # como una base de datos vacia
    conn = sqlite3.connect('ingreso.db')
    conn.execute("PRAGMA foreign_keys = 1")

    # Crear el cursor para poder ejecutar las querys
    c = conn.cursor()

    # Ejecutar una query
    c.execute("""
                DROP TABLE IF EXISTS ingresado;
            """)

    # Ejecutar una query
    c.execute("""
        CREATE TABLE ingresado (
            [codigo] INTEGER PRIMARY KEY,
            [empresa] STRING  NOT NULL,
            [actividad] STRING NOT NULL,
            [nombre] STRING NOT NULL,
            [edad] INTEGER NOT NULL,
            [dni] INTEGER  NOT NULL,
            [fecha_permiso] INTEGER NOT NULL, 
            [riesgo] STRING NOT NULL
        );
        """)

    # Para salvar los cambios realizados en la DB debemos
    # ejecutar el commit, NO olvidarse de este paso!
    conn.commit()

    # Cerrar la conexión con la base de datos
    conn.close()

def fill(codigo, empresa, actividad, nombre, edad, dni, fecha_permiso, riesgo):
    
    #Conecta con la BD
    conn = sqlite3.connect('ingreso.db')
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()

    values = [codigo, empresa, actividad, nombre, edad, dni, fecha_permiso, riesgo]

    try: 
        c.execute("""
            INSERT INTO ingresado (codigo, empresa, actividad, nombre, edad, dni, fecha_permiso, riesgo)
            VALUES (?,?,?,?,?,?,?,?);""", values)

    except sqlite3.IntegrityError:
        return print('Ya se encuentra registrado')

    conn.commit()
    # Cerrar la conexión con la base de datos
    conn.close()

def verifica(codigo):
    
    #Conecta con la BD
    conn = sqlite3.connect('ingreso.db')
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()

    c.execute("""SELECT codigo, empresa, actividad, nombre, edad, dni, fecha_permiso, riesgo
                FROM ingresado 
                WHERE codigo = ?;""", (codigo,))
    
    query_results = c.fetchall()

    conn.commit()
    # Cerrar la conexión con la base de datos
    conn.close()

    #Retorna los resultados obtenidos
    return query_results

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def report(limit=0, offset=0, dict_format=False):
    
    # Conectarse a la base de datos
    conn = sqlite3.connect(db['database'])
    if dict_format is True:
        conn.row_factory = dict_factory
    c = conn.cursor()

    query = 'SELECT codigo, empresa, actividad, nombre, edad, dni, fecha_permiso, riesgo FROM validacion'

    if limit > 0:
        query += ' LIMIT {}'.format(limit)
        if offset > 0:
            query += ' OFFSET {}'.format(offset)

    query += ';'

    c.execute(query)
    query_results = c.fetchall()

    # Cerrar la conexión con la base de datos
    conn.close()
    return query_results


def esquema_usuario():

    # Conectarnos a la base de datos
    # En caso de que no exista el archivo se genera
    # como una base de datos vacia
    conn = sqlite3.connect('usuarios.db')
    conn.execute("PRAGMA foreign_keys = 1")

    # Crear el cursor para poder ejecutar las querys
    c = conn.cursor()

    # Ejecutar una query
    c.execute("""
                DROP TABLE IF EXISTS usuario;
            """)

    # Ejecutar una query
    c.execute("""
        CREATE TABLE usuario (
            [Clave] INTEGER PRIMARY KEY,
            [Correo] STRING  NOT NULL,
            [Nombre] STRING  NOT NULL
        );
        """)

    # Para salvar los cambios realizados en la DB debemos
    # ejecutar el commit, NO olvidarse de este paso!
    conn.commit()

    # Cerrar la conexión con la base de datos
    conn.close()

def fill_usuario(correo, clave, nombre):
    
    conn = sqlite3.connect('usuarios.db')
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()

    values = [correo, clave, nombre]

    try: 
        c.execute("""
            INSERT INTO usuario (correo, clave, nombre)
            VALUES (?,?,?);""", values)

    except sqlite3.IntegrityError:
        return print('Ya se encuentra registrado')

    conn.commit()
    # Cerrar la conexión con la base de datos
    conn.close()


