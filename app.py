from flask import Flask
from flask_cors import CORS
from config import Config
from flask_jwt_extended import JWTManager
from utils.utils import db

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
JWTManager(app)
db.init_app(app)

try:
    
    from controller import chat_history_controller, user_controller, auth_controller
    app.register_blueprint(auth_controller.auth_bp)
    app.register_blueprint(user_controller.user_bp)
    app.register_blueprint(chat_history_controller.chat_history_bp)

    print(app.url_map)


    # crea las tablas de los modelos
    with app.app_context():
        db.create_all()
    
except Exception as e:
    print(f"Error: {e}")


if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)
