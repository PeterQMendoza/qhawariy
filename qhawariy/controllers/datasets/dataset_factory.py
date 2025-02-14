from __future__ import annotations
from abc import ABC,abstractmethod
import datetime
from typing import List,Any

import numpy as np
import pandas as pd

class IDataset(ABC):
    @abstractmethod
    def guardar(self):
        pass

class DatasetControl(IDataset):

    _dataframe:pd.DataFrame
    _viajes:pd.DataFrame
    _controls:pd.DataFrame

    def __init__(self,data:List,viajes:List,controles:List)->None:
        datas=[DatasetRoute.convert_to_dict(item) for item in data]
        self._dataframe=pd.DataFrame(datas)

        list_viajes=[DatasetRoute.convert_to_dict(item) for item in viajes]
        self._viajes=pd.DataFrame(list_viajes)

        list_controls=[DatasetRoute.convert_to_dict(item) for item in controles]
        self._controls=pd.DataFrame(list_controls)

    def proccess_dataframe(self)->None:
        aux=self._dataframe

        # Obtener los nombres de cada control
        ctrl=self._controls
        ctrl=ctrl.drop(columns=["id_control","latitud","longitud"])
        val=list(ctrl["codigo"].unique())
        times=val.copy()
        val.reverse()
        val.append("id_viaje")
        val.reverse()
        

        aux=aux.groupby("id_viaje").agg(lambda x:list(x)).reset_index()
        aux=aux.drop("id_ct",axis=1)
        aux=pd.concat([aux.drop("id_control",axis=1),aux["id_control"].apply(pd.Series)],axis=1)
        columns=aux.columns.to_list()
        tiempo=columns.index("tiempo")
        new_col=columns[tiempo+1:]
        aux=aux.drop(columns=new_col)
        aux=pd.concat([aux.drop("tiempo",axis=1),aux["tiempo"].apply(pd.Series)],axis=1)
        aux.columns=val


        col_times=aux[times]
        col_t=col_times.columns.to_list()
        for col in col_times:
            col_times[col]=pd.to_datetime(col_times[col].astype(str))
        aux[col_t]=col_times[col_t]

        # Para establacer el ordenamiento de la columnas
        # i=val[1]
        # if i in val:
        #     val.remove(i)
        #     val.append(i)
        # aux=aux[val]

        # fusionar con viajes
        aux=pd.merge(aux,self._viajes,on="id_viaje",how="inner")
        aux=aux.drop(columns=["orden"])
        # aux=pd.merge(aux,self._dataframe,on="id_viaje",how="inner")
        aux=aux.drop(columns=["id_vehiculo","id_programacion"])

        #
        aux=aux.dropna(how="all")
        aux=aux.fillna(value="")

        self._dataframe=aux

    def guardar(self):
        pass


class DatasetViaje(IDataset):
    _dataframe:pd.DataFrame
    _vehicles:pd.DataFrame

    def __init__(self,data:List,vehicles:List)->None:
        datas=[DatasetRoute.convert_to_dict(item) for item in data]
        self._dataframe=pd.DataFrame(datas)

        list_vehicles=[DatasetRoute.convert_to_dict(item) for item in vehicles]
        self._vehicles=pd.DataFrame(list_vehicles)

    def proccess_dataframe(self)->None:
        aux=self._dataframe

        # eliminar primera fila
        # aux=aux.drop(columns=['id_viaje'])

        #fusionar con vehiculos
        aux=pd.merge(aux,self._vehicles,on="id_vehiculo",how="inner")
        aux=aux.drop(columns=["id_vehiculo","placa","marca","modelo","fecha_fabricacion","numero_asientos","activo","estado","id_programacion"])

        aux=aux.dropna(how="all")
        aux=aux.fillna(value="")

        #Cambiar nombre de las columnas
        aux=aux.rename(columns={"flota":"vehiculo","orden":"o"})

        self._dataframe=aux

    def guardar(self):
        pass

class DatasetRoute(IDataset):
    _dataframe:pd.DataFrame
    _vehicles:pd.DataFrame
    _controles:pd.DataFrame
    
    def __init__(self,data:List,vehicles:List)->None:
        # Convertir lista a dataframe
        datas=[DatasetRoute.convert_to_dict(item) for item in data]
        self._dataframe=pd.DataFrame(datas)

        list_vehicles=[DatasetRoute.convert_to_dict(item) for item in vehicles]
        self._vehicles=pd.DataFrame(list_vehicles)
    
        
    def guardar(self):
        pass

    @staticmethod
    def convert_to_dict(row)->dict:
        if row is None:
            return None
        
        return_dict=dict()
        keys=row.__table__.columns.keys()
        for key in keys:
            return_dict[key]=getattr(row,key)
        return return_dict
    
    @staticmethod
    def convert_timedelta_to_time(td:datetime.timedelta)->datetime.time:
        total_seconds=td.total_seconds()
        hours=int(total_seconds//3600)
        minutes=int((total_seconds%3600)//60)
        seconds=int(total_seconds%60)
        return datetime.time(hours,minutes,seconds)

    @staticmethod
    def formating_time(time:datetime.time)->str:
        hour=''
        minute=''
        second=''
        if time.hour>0:
            hour=f"{time.hour} hr"
        if time.minute>0:
            minute=f"{time.minute} min"
        if time.second>0:
            second=f"{time.second} s"
        if time.hour==0 and time.minute==0 and time.second==0:
            second=f"{time.second} s"
        return hour+minute+second
    
    @staticmethod
    def time_to_seconds(time:datetime.time)->int:
        hour=0
        minute=0
        second=0
        if time.hour>0:
            hour=time.hour*3600
        if time.minute>0:
            minute=time.minute*60
        if time.second>0:
            second=time.second
        return hour+minute+second

    
    @staticmethod
    def color_negative_red(x,color)->str:
        return np.where(x > 300, f"color: {color};font-weight: bold", None)
    
    @staticmethod
    def icon_based_on_value(value):
        _icon_up:str='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="20px" height="20px" type="image/svg+xml"><path fill="#05be50" d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM385 231c9.4 9.4 9.4 24.6 0 33.9s-24.6 9.4-33.9 0l-71-71V376c0 13.3-10.7 24-24 24s-24-10.7-24-24V193.9l-71 71c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9L239 119c9.4-9.4 24.6-9.4 33.9 0L385 231z"/></svg>'
        _icon_down:str='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="20px" height="20px"  type="image/svg+xml"><path fill="#EB0046D9" d="M256 0a256 256 0 1 0 0 512A256 256 0 1 0 256 0zM127 281c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l71 71L232 136c0-13.3 10.7-24 24-24s24 10.7 24 24l0 182.1 71-71c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9L273 393c-9.4 9.4-24.6 9.4-33.9 0L127 281z"/></svg>'

        if value>0:
            return _icon_up
        elif value<0:
            return _icon_down
    
    @staticmethod
    def state_based_on_value(value):
        _to_time:str='<div class="flex items-center justify-center"><span class="a_tiempo cuadro"><div class="mark">A tiempo</div></span></div>'
        _time_less:str='<div class="flex items-center justify-center"><span class="retrasado cuadro"><div class="mark">retrasado</div></span></div>'

        if value>0:
            return _to_time
        elif value<0:
            return _time_less
    
    def process_dataframe(self):
        aux=self._dataframe
        #ordenar la dataframe por el tiempo
        aux=aux.sort_values(by="tiempo")
        aux["tiempo"]=pd.to_datetime(aux["tiempo"].astype(str))
        # Eliminar primera columna
        aux=aux.drop(columns=['id_vp'])

        #fusionar con vehiculos
        aux=pd.merge(aux,self._vehicles,on="id_vehiculo",how="inner")
        aux=aux.drop(columns=["id_vehiculo","placa","marca","modelo","fecha_fabricacion","numero_asientos","activo","estado","id_programacion"])

        # Cambiar orden de las columnas
        aux=aux.reindex(columns=["flota","tiempo"])

        # Aumentar la llegada programada aproximado#
        demora=datetime.timedelta(minutes=75)
        aux["llegada"]=pd.to_datetime(aux.tiempo.astype(str))
        aux["llegada"]=aux.llegada+demora
        # aux.llegada=aux.llegada.dt.time

        # Determinar la frecuencia
        aux["frecuencia"]=pd.to_datetime(aux.llegada.astype(str))
        aux.frecuencia=aux.frecuencia-aux.frecuencia.shift(1)
        aux=aux.dropna(how="all")
        aux=aux.fillna(value=datetime.timedelta(seconds=0))
        aux.frecuencia=aux.frecuencia.apply(DatasetRoute.convert_timedelta_to_time)
        aux["segundos"]=aux.frecuencia.apply(DatasetRoute.time_to_seconds)
        aux["icon"]=aux.segundos.apply(DatasetRoute.icon_based_on_value)
        # aux.style.apply(DatasetRoute.color_negative_red,subset=['segundos'])
        aux.frecuencia=aux.frecuencia.apply(DatasetRoute.formating_time)

        #Cambiar nombre de las columnas
        aux=aux.rename(columns={"flota":"vehiculo"})
        aux=aux.rename(columns={"tiempo":"salida"})
        aux=aux.rename(columns={"llegada":"programada"})

        aux=aux.dropna(how="all")
        aux=aux.fillna(value="")
        
        # restablecer los index
        aux=aux.reset_index(drop=True)

        # escribir los cambios para dataframe
        # aux=aux.style.apply(DatasetRoute.color_negative_red,color="red",subset=['segundos'])
        self._dataframe=aux





# Clases creadoras
class Factory(ABC):
    def __init__(self)->None:
        pass

    def create_dataset(self)->IDataset:
        pass

class DatasetFactory(Factory):
    def create_dataset(self,data:List,vehicles:List):
        dataset=DatasetRoute(data,vehicles)
        return dataset
        
class DatasetViajeFactory(Factory):
    def create_dataset(self,data:List,vehicles:List) -> IDataset:
        dataset=DatasetViaje(data,vehicles)
        return dataset
    
class DatasetControlFactory(Factory):
    def create_dataset(self,data:List,viajes:List,controles:List) -> IDataset:
        dataset=DatasetControl(data,viajes,controles)
        return dataset
