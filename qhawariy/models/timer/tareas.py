import datetime
import time
from qhawariy import scheduler
from qhawariy.models.timer.qh_timer import Flota,Reloj
from qhawariy.models.vehiculo_programado import VehiculoProgramado
from qhawariy.utilities.builtins import LIMA_TZ

# @scheduler.task('cron',id="hora_trabajo",day=1,max_instances=1,start_date="2024-09-10 10:33:00")
# def horarios_trabajo():
#     pass

# @scheduler.task("interval",id="job_sync",seconds=75,max_instances=1,start_date="2024-09-10 10:33:00",end_date="2024-09-10 10:36:00")
# def actualizar_estado_vehiculos():
#     """Tarea utilizada para actualizar la estado de vehiculos"""
#     # ahora=datetime.datetime.now(LIMA_TZ)
#     # desde=datetime.datetime(year=ahora.year,month=ahora.month,day=ahora.day,hour=0,minute=0,second=0)-datetime.timedelta(days=148)
#     # hasta=desde-datetime.timedelta(days=1)
#     # with scheduler.app.app_context():
#     #     vehiculos=VehiculoProgramado.obtener_todos_vp_fecha(desde=desde,hasta=hasta)
#     #     lista_vehiculos=[v.vehiculo for v in vehiculos]
#     #     flota=Flota(lista_vehiculos)
#     #     flota.establecer_vehiculos_en_programado(lista_vehiculos[0])
#     #     print(flota._flota[0])
#     ahora=datetime.datetime.now(tz=LIMA_TZ)
#     desde=datetime.datetime(year=ahora.year,month=ahora.month,day=ahora.day,hour=0,minute=0,second=0)-datetime.timedelta(days=150)
#     with scheduler.app.app_context():
#         vehiculos=VehiculoProgramado.obtener_todos_vp_fecha(desde,desde)
#         lista_vehiculos=[v.vehiculo for v in vehiculos]
#         #Actualizar estado de vehiculos
#         for v in lista_vehiculos:
#             v.actualizar()
#         flota=Flota(lista_vehiculos)
#         flota.establecer_vehiculos_en_programado(lista_vehiculos[0])
#         print(flota._flota[0])