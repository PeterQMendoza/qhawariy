
import datetime
import os
import random

import pandas as pd
import geopandas as gpd

from os import walk

from flask import current_app

from openpyxl.styles import (NamedStyle,PatternFill,Border,Side,Alignment,Protection,Font,Color,NumberFormatDescriptor)

from qhawariy.utilities import builtins

def convertir_DataFrame(list):
    data_list = [a_dict(item) for item in list]
    df = pd.DataFrame(data_list)
    return df

def a_dict(row):
    if row is None:
        return None

    rtn_dict = dict()
    keys = row.__table__.columns.keys()
    for key in keys:
        rtn_dict[key] = getattr(row, key)
    return rtn_dict

def archivo_existe(ruta):
    return os.path.exists(ruta)

def hacer_arbol(path):
    fn = []
    for (dirpath, dirnames, filenames) in walk(path):
        fn.extend(filenames)
        break
    
    return fn

def generar_numero(lenght=8):
    """Genera numero pseudoaleatorio"""
    return ''.join([str(random.randint(0,9)) for i in range(lenght)])

def obtener_tiempo_actual():
    pass


#Clase Calendario
class Calendario():
    """
    Clase Calendario: Devuelve una lista del modelo Fecha, para ser mostrados e una plantilla
    """
    def __init__(self,year,month,lista_fechas,primer_dia_lista,primer_dia_semana):
        self.year=year
        self.month=month
        self.actual=datetime.date(year=year,month=month,day=primer_dia_lista)
        self.ultimo=datetime.date(year=year,month=month+1,day=1)-datetime.timedelta(days=1)
        self.primer_dia_semana=primer_dia_semana
        self.ultimo_dia_mes=self.ultimo.day
        self.dia=0
        self.dia_actual=0
        self.ultima_celda=self.primer_dia_semana+self.ultimo_dia_mes
        self.fechas=[]
        

        # Para busqueda por dias no continuas
        lista_dias=[]
        for a in lista_fechas:
            if getattr(a,"fecha"):
                lista_dias.append(getattr(a,"fecha").day)

        # Agregando 42 celdas de 6 filas(semanas) y de 7 columnas(dias)
        for i in range(1,43):
            if i==self.primer_dia_semana:
                self.dia=1
            if i<self.primer_dia_semana or i>=self.ultima_celda:
                self.fechas.append(str(''))
            else:
                if self.dia in lista_dias:
                    index=lista_dias.index(self.dia)
                    self.fechas.append(lista_fechas[index])#
                else:
                    self.fechas.append(str(self.dia))
                self.dia=self.dia+1
            if i%7==0:
                if self.dia>self.ultimo_dia_mes:
                    break

