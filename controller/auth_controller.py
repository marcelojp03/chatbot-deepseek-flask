from flask import Blueprint, request, jsonify
from repository.user_repository import UserRepository
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from datetime import datetime
from utils.responses import Responses

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
userRepository = UserRepository()
bcrypt = Bcrypt()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        response = Responses.error(
            code = 1,
            description = 'Correo y contraseña son obligatorios'
        )
    
        return jsonify(response)
    user = userRepository.get_by_email(email)

    if user and bcrypt.check_password_hash(user['password'], password):
    # if usuario and contraseña=="admin":    
        access_token = create_access_token(
            identity = user['id']
            )
        # access_token = "TOKEN"
        response = Responses.jwt(
            code = 0,
            data = user,
            accessToken = access_token,
            description = 'Credenciales validadas correctamente'
        )
        return jsonify(response)
    else:
        response = Responses.error(
            code = 1,
            description = 'Credenciales inválidas'
        )
        return jsonify(response)
    
@auth_bp.route('/register', methods=['POST'])
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
    
@auth_bp.route('/token-expiration', methods=['GET'])
@jwt_required()
def token_expiration():
    # Obtener la información del JWT
    jwt_data = get_jwt()
    # Obtener el tiempo de expiración (en Unix timestamp)
    expiration_timestamp = jwt_data['exp']
    
    # Convertir el timestamp de expiración a un formato legible
    expiration_time = datetime.fromtimestamp(expiration_timestamp)
    
    # Calcular el tiempo restante
    current_time = datetime.utcnow()
    remaining_time = expiration_time - current_time

    return jsonify({"expira_en": f"{remaining_time.seconds // 60} minutos"})