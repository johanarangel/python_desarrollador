#!/usr/bin/env python
'''
Config
---------------------------
Autor: Johana Rangel
Version: 1.0

Descripcion:
Este programa fue creado para leer archivos de configuracion
'''

__author__ = "Johana Rangel"
__email__ = "johanarang@hotmail.com"
__version__ = "1.0"

from configparser import ConfigParser


def config(section, filename='config.ini'):
    # Read config file
    parser = ConfigParser()
    parser.read(filename)

    # Read section
    config_param = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config_param[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config_param