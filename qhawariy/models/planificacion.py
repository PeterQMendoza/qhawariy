
"""
Modulo que administra los Modelos: 
 1. Usuario
 2. Rol
 3. UsuarioRol
 4. Programacion
 5. Ruta
 6. Viaje
 7. Vehiculo
 8. Gasto
 9. TipoGasto
 10. ClasificadorVariable
 11. Ingreso.
"""
import pytz

from datetime import datetime

from email.policy import default
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

from qhawariy import db

# import qhawariy.models.control
# import qhawariy.models.financiero

lima_tz=pytz.timezone('America/Lima')

class Usuario(db.Model,UserMixin):
    """
    Modelo Usuario define a todos los usuarios que pertencen e ingresan al sistema
    """
    __tablename__="usuarios"
    id_usuario=db.Column(db.Integer,primary_key=True)
    nombres=db.Column(db.String(50),nullable=False)
    apellidos=db.Column(db.String(50),nullable=False)
    dni=db.Column(db.String(15),unique=True,nullable=False)
    telefono=db.Column(db.String(15),nullable=False)
    correo_electronico=db.Column(db.String(50), unique=True, nullable=False)
    fecha_registro=db.Column(db.DateTime,default=datetime.now(tz=lima_tz))
    clave=db.Column(db.String(128), nullable=False)

    # Relaciones
    uroles=db.relationship("UsuarioRol",back_populates="usuario",cascade="all,delete-orphan")
    # propietarios=db.relationship("Vehiculo",back_populates="propietario",cascade="all,delete-orphan")
    # conductores=db.relationship("Vehiculo",back_populates="conductor",cascade="all,delete-orphan")
    # ayudantes=db.relationship("Vehiculo",back_populates="ayudante",cascade="all,delete-orphan")
    iusuarios=db.relationship("Ingreso",back_populates="usuario",cascade="all,delete-orphan")
    reportantes=db.relationship("InspeccionReportante",back_populates="reportante",cascade="all,delete-orphan")
    uincidencias=db.relationship("UsuarioIncidencia",back_populates="uincidencia",cascade="all,delete-orphan")
    pasajeros=db.relationship("ViajePasajero",back_populates="vpasajero",cascade="all,delete-orphan")
    ipropietarios=db.relationship("InspeccionPropietario",back_populates="ipropietario",cascade="all,delete-orphan")
    usuarios=db.relationship("GastoUsuario",back_populates="usuario",cascade="all,delete-orphan")

    def __init__(self, nombres,apellidos,dni,telefono,correo_electronico):
        self.id=self.id_usuario
        self.nombres=nombres
        self.apellidos=apellidos
        self.dni=dni
        self.telefono=telefono
        self.correo_electronico=correo_electronico
        self.fecha_registro=datetime.now(tz=lima_tz)
   

    def __repr__(self):
        return f'<Usuaurio {self.email}>'

    def establecer_clave(self, clave):
        self.clave = generate_password_hash(clave)

    def revisar_clave(self, clave):
        return check_password_hash(self.clave, clave)
    
    # Para reconocer la id i registrar usuario en Login_Manager
    # Revisar la documentacion de Flask_login para establecer si
    # el usuario cambia de clave
    def get_id(self):
        return self.id_usuario

    def guardar(self):
        if not self.id_usuario:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_usuario_por_id(id):
        return Usuario.query.get(id)

    @staticmethod
    def obtener_usuario_por_nombre(nombre):
        return Usuario.query.filter_by(nombre=nombre)

    @staticmethod
    def obtener_usuario_por_correo_electronico(correo_electronico):
        return Usuario.query.filter_by(correo_electronico=correo_electronico).first()

    @staticmethod
    def obtener_todos_usuarios():
        return Usuario.query.all()
    
class Rol(db.Model):
    """
    Modelo Rol describe el rol que se asignara al usuario
    """
    __tablename__="roles"
    id_rol=db.Column(db.Integer,primary_key=True)
    rol=db.Column(db.String(20),unique=True,nullable=False)

    # Relaciones
    rusuarios=db.relationship("UsuarioRol",back_populates="rol",cascade="all,delete-orphan")

    def __init__(self, rol):
        self.rol=rol

    def __repr__(self):
        return f'<Rol {self.rol}>'

    def guardar(self):
        if not self.id_rol:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_rol_por_id(id):
        return Rol.query.get(id)

    @staticmethod
    def obtener_todos_roles():
        return Rol.query.all()
    
    @staticmethod
    def obtener_rol_por_nombrerol(rol):
        return Rol.query.filter_by(rol=rol)
    
# Crea una tabla de union Usuario/Rol
class UsuarioRol(db.Model):
    """
    Modelo UsuarioRol crea una relacion de tablas union entre Usuario y Rol
    """
    __tablename__="usuarios_roles"
    id_ur=db.Column(db.Integer,primary_key=True)
    id_usuario=db.Column(db.Integer,db.ForeignKey("usuarios.id_usuario"),nullable=False)
    id_rol=db.Column(db.Integer,db.ForeignKey("roles.id_rol"),nullable=False)

    #Establecer relaciones de uno a muchos
    usuario=db.relationship("Usuario",back_populates="uroles",uselist=False,single_parent=True)
    rol=db.relationship("Rol",back_populates="rusuarios",uselist=False,single_parent=True)

    def __init__(self,id_usuario,id_rol):
        self.id_usuario=id_usuario
        self.id_rol=id_rol

    def __repr__(self):
        return f'<UsuarioRol {self.id_ur}>'

    def guardar(self):
        if not self.id_ur:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_urol_por_id(id):
        return UsuarioRol.query.get(id)

    @staticmethod
    def obtener_todos_uroles():
        return UsuarioRol.query.all()

    @staticmethod
    def obtener_usuarios_por_idrol(idrol):
        return UsuarioRol.query.query.filter_by(id_rol=idrol)
    
    @staticmethod
    def obtener_todos_propietarios():
        pro=UsuarioRol.query.all()
        prop=[]
        for p in pro:
            rp=Rol.obtener_rol_por_id(p.id_rol)
            if rp.rol=="propietario":
                user=Usuario.obtener_usuario_por_id(p.id_usuario)
                prop.append(user)
        return prop
    
    @staticmethod
    def obtener_todos_conductores():
        pro=UsuarioRol.query.all()
        prop=[]
        for p in pro:
            rp=Rol.obtener_rol_por_id(p.id_rol)
            if rp.rol=="conductor":
                user=Usuario.obtener_usuario_por_id(p.id_usuario)
                prop.append(user)
        return prop
    
    @staticmethod
    def obtener_todos_ayudantess():
        pro=UsuarioRol.query.all()
        prop=[]
        for p in pro:
            rp=Rol.obtener_rol_por_id(p.id_rol)
            if rp.rol=="ayudante":
                user=Usuario.obtener_usuario_por_id(p.id_usuario)
                prop.append(user)
        return prop
    
    @staticmethod
    def obtener_id_rol_usuario(idusuario):
        return UsuarioRol.query.filter_by(id_usuario=idusuario).first()
    
class Programacion(db.Model):
    """
    Modelo Programacion
    """
    __tablename__="programaciones"
    id_programacion=db.Column(db.Integer,primary_key=True)
    fecha_programa=db.Column(db.DateTime,default=datetime.now(tz=lima_tz))
    tiempo=db.Column(db.Time,default=datetime.now(tz=lima_tz).time())
    id_ruta=db.Column(db.Integer,db.ForeignKey("rutas.id_ruta"),nullable=False)

    #Establecer relaciones {Table1}*1-->1{Table2}
    ruta=db.relationship("Ruta",back_populates="rutas",uselist=False,single_parent=True)

    #Establecer relacion inversa {Tabla2}*1-->1{Tabla1}
    viajes=db.relationship("Viaje",back_populates="programacion",cascade="all,delete-orphan")
    programaciones=db.relationship("VehiculoProgramado",back_populates="programa",cascade="all,delete-orphan")

    def __init__(self,tiempo,id_vehiculo,id_ruta):
        self.tiempo=tiempo
        self.id_vehiculo=id_vehiculo
        self.id_ruta=id_ruta

    def __repr__(self):
        return f'<Programacion {self.id_programacion}>'

    def guardar(self):
        if not self.id_programacion:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_rol_por_id(id):
        return Programacion.query.get(id)

    @staticmethod
    def obtener_todos_roles():
        return Programacion.query.all()
    
class VehiculoProgramado(db.Model):
    """
    Modelo VehiculoProgramado
    """
    __tablename__="vehiculo_programados"
    id_vp=db.Column(db.Integer,primary_key=True)
    id_vehiculo=db.Column(db.Integer,db.ForeignKey("vehiculos.id_vehiculo"),nullable=False)
    id_programacion=db.Column(db.Integer,db.ForeignKey("programaciones.id_programacion"),nullable=False)

    #Establecer relaciones {Table1}*1-->1{Table2}
    vehiculop=db.relationship("Vehiculo",back_populates="vehiculos",uselist=False,single_parent=True)
    programa=db.relationship("Programacion",back_populates="programaciones",uselist=False,single_parent=True)

    #Establecer relacion inversa {Tabla2}*1-->1{Tabla1}

    def __init__(self,id_vehiculo,id_programacion):
        self.id_vehiculo=id_vehiculo
        self.id_programacion=id_programacion

    def __repr__(self):
        return f'<VehiculoProgramado {self.id_vp}>'

    def guardar(self):
        if not self.id_vp:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_rol_por_id(id):
        return VehiculoProgramado.query.get(id)

    @staticmethod
    def obtener_todos_roles():
        return VehiculoProgramado.query.all()



class Ruta(db.Model):
    """
    Modelo Ruta
    """
    __tablename__="rutas"
    id_ruta=db.Column(db.Integer,primary_key=True)
    lugar_origen=db.Column(db.String(20),unique=True,nullable=False)
    lugar_destino=db.Column(db.String(20),unique=True,nullable=False)

    # Relaciones
    rutas=db.relationship("Programacion",back_populates="ruta",cascade="all,delete-orphan")

    def __init__(self, lugar_origen,lugar_destino):
        self.lugar_origen=lugar_origen
        self.lugar_destino=lugar_destino

    def __repr__(self):
        return f'<Ruta {self.id_ruta}>'

    def guardar(self):
        if not self.id_rol:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_ruta_por_id(id):
        return Ruta.query.get(id)

    @staticmethod
    def obtener_todos_rutas():
        return Ruta.query.all()

    @staticmethod
    def obtener_por_origen_destino(origen,destino):
        return Ruta.query.filter_by(lugar_origen=origen,lugar_destino=destino).first()
    
class Viaje(db.Model):
    """"
    Modelo Viaje
    """
    __tablename__="viajes"
    id_viaje=db.Column(db.Integer,primary_key=True)
    tiempo_salida=db.Column(db.Time,default=datetime.now(tz=lima_tz).time())
    tiempo_llegada=db.Column(db.Time,default=datetime.now(tz=lima_tz).time())
    id_programacion=db.Column(db.Integer,db.ForeignKey("programaciones.id_programacion"),nullable=False)

    #Establecer relaciones de {Tabla1}*1-->1{Tabla2}
    programacion=db.relationship("Programacion",back_populates="viajes",uselist=False,single_parent=True)
    
    #Establecer relacion inversa {Tabla2}*1-->1{Tabla1}
    viajesi=db.relationship("ViajeIncidencia",back_populates="viaje",cascade="all,delete-orphan")
    viajes=db.relationship("ViajePasajero",back_populates="viajep",cascade="all,delete-orphan")


    def __init__(self,tiempo_salida,tiempo_llegada,id_programacion):
        self.tiempo_salida=tiempo_salida
        self.tiempo_llegada=tiempo_llegada
        self.id_programacion=id_programacion

    def __repr__(self):
        return f'<Viaje {self.id_viaje}>'

    def guardar(self):
        if not self.id_ur:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_rol_por_id(id):
        return Viaje.query.get(id)

    @staticmethod
    def obtener_todos_roles():
        return Viaje.query.all()

class Vehiculo(db.Model):
    """"
    Modelo Vehiculo de administracion de vehiculos
    """
    __tablename__="vehiculos"
    id_vehiculo=db.Column(db.Integer,primary_key=True)
    placa=db.Column(db.String(8),unique=True,nullable=False)
    marca=db.Column(db.String(45),nullable=False)
    modelo=db.Column(db.String(45),nullable=False)
    fecha_fabricacion=db.Column(db.DateTime,default=datetime.now(tz=lima_tz))
    numero_asientos=db.Column(db.Integer,nullable=False)
    id_propietario=db.Column(db.Integer,db.ForeignKey("usuarios.id_usuario",ondelete="CASCADE"),nullable=False)
    id_conductor=db.Column(db.Integer,db.ForeignKey("usuarios.id_usuario",ondelete="CASCADE"),nullable=False)
    id_ayudante=db.Column(db.Integer,db.ForeignKey("usuarios.id_usuario",ondelete="CASCADE"),nullable=False)

    #Establecer relaciones de {Tabla1}*1-->1{Tabla2}
    # propietario=db.relationship("Usuario",back_populates="propietarios",uselist=False,single_parent=True)
    # conductor=db.relationship("Usuario",back_populates="conductores",uselist=False,single_parent=True)
    # ayudante=db.relationship("Usuario",back_populates="ayudantes",uselist=False,single_parent=True)

    #Establecer relacion inversa {Tabla2}*1-->1{Tabla1}
    mvehiculos=db.relationship("VehiculoMantenimiento",back_populates="vehiculo",cascade="all,delete-orphan")
    vehiculos=db.relationship("Programacion",back_populates="vehiculop",cascade="all,delete-orphan")
    dvehiculos=db.relationship("VehiculoDispositivo",back_populates="vehiculo",cascade="all,delete-orphan")
    ivehiculos=db.relationship("InspeccionVehiculo",back_populates="vehiculo",cascade="all,delete-orphan")


    def __init__(self,placa,marca,modelo,fecha_fabricacion,numero_asientos,id_propietario,id_conductor,id_ayudante):
        self.placa=placa
        self.marca=marca
        self.modelo=modelo
        self.fecha_fabricacion=fecha_fabricacion
        self.numero_asientos=numero_asientos
        self.id_propietario=id_propietario
        self.id_conductor=id_conductor
        self.id_ayudante=id_ayudante

    def __repr__(self):
        return f'<Vehiculo {self.id_vehiculo}>'

    def guardar(self):
        if not self.id_vehiculo:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_vehiculo_por_id(id):
        return Vehiculo.query.get(id)

    @staticmethod
    def obtener_todos_vehiculos():
        return Vehiculo.query.all()

    @staticmethod
    def obtener_vehiculo_por_placa(placa):
        return Vehiculo.query.filter_by(placa=placa).first()
    
class Gasto(db.Model):
    """
    Modelo Gasto
    """
    __tablename__="gastos"
    id_gasto=db.Column(db.Integer,primary_key=True)
    monto=db.Column(db.Numeric(precision=8,scale=2, asdecimal=True, decimal_return_scale=2),nullable=False)
    fecha_gasto=db.Column(db.DateTime,default=datetime.now(tz=lima_tz))
    descripcion=db.Column(db.String(50),nullable=False)
    id_cv=db.Column(db.Integer,db.ForeignKey("clasificadores_variables.id_cv"),nullable=False)
    id_tg=db.Column(db.Integer,db.ForeignKey("tipos_gastos.id_tg"),nullable=False)

    #Establecer relaciones de {Tabla1}*1-->1{Tabla2}
    tgasto=db.relationship("TipoGasto",back_populates="tiposg",uselist=False,single_parent=True)
    cvariable=db.relationship("ClasificadorVariable",back_populates="cvariablesg",uselist=False,single_parent=True)
    
    #Establecer relacion inversa {Tabla2}*1-->1{Tabla1}
    gusuarios=db.relationship("GastoUsuario",back_populates="gastou",cascade="all,delete-orphan")
    

    def __init__(self,monto,fecha_gasto,descripcion,id_cv,id_tg):
        self.monto=monto
        self.fecha_gasto=fecha_gasto
        self.descripcion=descripcion
        self.id_cv=id_cv
        self.id_tg=id_tg

    def __repr__(self):
        return f'<Gasto {self.id_gasto}>'

    def guardar(self):
        if not self.id_ur:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_rol_por_id(id):
        return Gasto.query.get(id)

    @staticmethod
    def obtener_todos_roles():
        return Gasto.query.all()
    
class TipoGasto(db.Model):
    """
    Modelo Gasto
    """
    __tablename__="tipos_gastos"
    id_tg=db.Column(db.Integer,primary_key=True)
    tipo=db.Column(db.String(20),nullable=False)

    #Establecer relacion inversa {Tabla2}*1-->1{Tabla1}
    tiposg=db.relationship("Gasto",back_populates="tgasto",cascade="all,delete-orphan")
    

    def __init__(self,tipo):
        self.tipo=tipo

    def __repr__(self):
        return f'<TipoGasto {self.id_tg}>'

    def guardar(self):
        if not self.id_ur:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_rol_por_id(id):
        return TipoGasto.query.get(id)

    @staticmethod
    def obtener_todos_roles():
        return TipoGasto.query.all()
    
class ClasificadorVariable(db.Model):
    """
    Modelo Gasto
    """
    __tablename__="clasificadores_variables"
    id_cv=db.Column(db.Integer,primary_key=True)
    tipo=db.Column(db.String(20),nullable=False)

    #Establecer relacion inversa {Tabla2}*1-->1{Tabla1}
    cvariablesg=db.relationship("Gasto",back_populates="cvariable",cascade="all,delete-orphan")
    cvariables=db.relationship("Ingreso",back_populates="cvariable",cascade="all,delete-orphan")
    

    def __init__(self,tipo):
        self.tipo=tipo

    def __repr__(self):
        return f'<ClasificadorVariable {self.id_cv}>'

    def guardar(self):
        if not self.id_ur:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_rol_por_id(id):
        return ClasificadorVariable.query.get(id)

    @staticmethod
    def obtener_todos_roles():
        return ClasificadorVariable.query.all()

class Ingreso(db.Model):
    """
    Modelo Ingreso
    """
    __tablename__="ingresos"
    id_ingreso=db.Column(db.Integer,primary_key=True)
    id_cv=db.Column(db.Integer,db.ForeignKey("clasificadores_variables.id_cv"),nullable=False)
    id_usuario=db.Column(db.Integer,db.ForeignKey("usuarios.id_usuario"),nullable=False)

    #Establecer relaciones de {Tabla1}*1-->1{Tabla2}
    usuario=db.relationship("Usuario",back_populates="iusuarios",uselist=False,single_parent=True)
    cvariable=db.relationship("ClasificadorVariable",back_populates="cvariables",uselist=False,single_parent=True)
    
    #Establecer relacion inversa {Tabla2}*1-->1{Tabla1}
    iptransportes=db.relationship("IngresoPagoTransporte",back_populates="ingreso",cascade="all,delete-orphan")
    iptramites=db.relationship("IngresoPagoTramite",back_populates="ingreso",cascade="all,delete-orphan")
    

    def __init__(self,id_cv,id_usuario):
        self.id_cv=id_cv
        self.id_usuario=id_usuario

    def __repr__(self):
        return f'<Ingreso {self.id_ingreso}>'

    def guardar(self):
        if not self.id_ur:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_rol_por_id(id):
        return Ingreso.query.get(id)

    @staticmethod
    def obtener_todos_roles():
        return Ingreso.query.all()
    