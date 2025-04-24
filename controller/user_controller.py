from flask import Blueprint, request, jsonify
from repository.user_repository import UserRepository
from utils.responses import Responses
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_bcrypt import Bcrypt

user_bp = Blueprint('user', __name__, url_prefix='/api/users')
userRepository = UserRepository()
bcrypt = Bcrypt()

@user_bp.route('/listar', methods=['GET'])
# @jwt_required()
def get_all_users():
    users = userRepository.get_all()
    response = Responses.success(
        code = 0,
        data = users,
        description = 'Usuarios listados correctamente'
    )
    return jsonify(response)

@user_bp.route('/buscar/<int:user_id>', methods=['GET'])
# @jwt_required()
def get_user_by_id(user_id):
    user = userRepository.get_by_id(user_id)
    if user:
        response = Responses.success(
            code = 0,
            data = user,
            description = 'Usuario encontrado'
        )
        return jsonify(response)
    else:
        response = Responses.error(
            code = 0,
            description = f'Usuario con ID {user_id} no encontrado'
        )
        return jsonify(response)

@user_bp.route('/register', methods=['POST'])
# @jwt_required()
def create_user():
    data = request.json
    name = data.get('name')
    lastname = data.get('lastname')
    email = data.get('email')
    password = data.get('password')
    password_hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    phone = data.get('phone')
    photo = data.get('photo')

    if name and lastname and email and password_hashed:
        newUser = userRepository.create(
            name=name,
            lastname=lastname,
            email=email,
            password=password_hashed, 
            phone=phone,
            photo=photo,
        )
        if newUser:
            response = Responses.success(
                code = 0,
                data = newUser,
                description = 'Usuario creado correctamente'
            )   
            return jsonify(response)
    else:
        return jsonify(Responses.error('Nombre de usuario, contraseña, nombre y correo son obligatorios'))
    

@user_bp.route('/eliminar-permanente/<int:usuario_id>', methods=['DELETE'])
@jwt_required()
def delete_user_per(usuario_id):
    usuario_eliminado = userRepository.deletePer(usuario_id)
    if usuario_eliminado:
        return jsonify(Responses.success(usuario_eliminado))
    else:
        return jsonify(Responses.error(f'Usuario con ID {usuario_id} no encontrado'))
    
    
@user_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected_route():
    current_user_id = get_jwt_identity()  # Obtener la identidad del token
    return jsonify(message=f"This is a protected route. Current user ID: {current_user_id}")