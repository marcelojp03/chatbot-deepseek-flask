from app import db
from flask import current_app
from model.user import User
import base64
import os

class UserRepository:
    def get_all(self):
        users = User.query.all()
        return [user.serialize() for user in users]

    def get_by_id(self, user_id):
        user = User.query.get(user_id)
        if user:
            usuario_serializado = user.serialize()
            photo = user.photo
            if photo:
                ruta_imagen = os.path.join(current_app.config['IMAGENES_USUARIOS_CARPETA'], photo)
                with open(ruta_imagen, 'rb') as f:
                    imagen_bytes = f.read()
                    imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
                usuario_serializado['photo'] = imagen_base64
            return usuario_serializado
        else:
            return None
    
    def get_by_name(self, name):
        user=User.query.filter_by(name=name).first()
        return user.serialize() if user else None
    
    def get_by_email(self, email):
        usuario = User.query.filter_by(email=email).first()
        return usuario.serialize() if usuario else None

    def create(self, name, lastname, email, password, phone = None, photo=None):
        newUser = User(
            name=name,
            lastname=lastname,
            email=email,
            password=password,
            phone = phone,
            photo=photo        
        )
        db.session.add(newUser)
        db.session.commit()
        return newUser.serialize()

    def update(self, usuario_id, nombre_usuario, contraseña, nombre, correo, foto_base64=None):
        usuario = User.query.get(usuario_id)
        
        if usuario:
            usuario.nombre_usuario = nombre_usuario
            usuario.nombre = nombre
            usuario.correo = correo
            if contraseña:
                usuario.contraseña = contraseña

            if foto_base64:
                foto=self.guardar_imagen_local(foto_base64,usuario_id)
                usuario.foto = foto

            db.session.commit()

        return usuario.serialize() if usuario else None

    def delete(self, usuario_id):
        usuario = User.query.get(usuario_id)
        if usuario:
            #db.session.delete(usuario)
            usuario.estado=False
            db.session.commit()

        return usuario.serialize() if usuario else None
    
    def deletePer(self, usuario_id):
        usuario = User.query.get(usuario_id)
        if usuario:
            db.session.delete(usuario)
            #usuario.estado=False
            db.session.commit()

        return usuario.serialize() if usuario else None
