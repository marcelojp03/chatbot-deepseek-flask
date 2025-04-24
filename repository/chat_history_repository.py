from app import db
from model.chat_history import ChatHistory


class ChatHistoryRepository:
    def get_all(self):
        chats_history = ChatHistory.query.all()
        return [chat_history.serialize() for chat_history in chats_history]

    def get_by_user_id(self, user_id):
        user_chats = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.created_at.asc()).all()
        return [user_chat.serialize() for user_chat in user_chats]
    
    def get_by_user_id_last_message(self, user_id, limit = 1):
        user_chats = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.created_at.desc()).limit(limit).all()
        return [user_chat.serialize() for user_chat in user_chats]


    def create(self, user_id, user_message, assistant_response):
        newChatHistory = ChatHistory(
            user_id = user_id,
            user_message = user_message,
            assistant_response = assistant_response
        )
        db.session.add(newChatHistory)
        db.session.commit()
        return newChatHistory.serialize()

    def update(self, usuario_id, nombre_usuario, contraseña, nombre, correo, foto_base64=None):
        usuario = ChatHistory.query.get(usuario_id)
        
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

    def delete(self, user_id):
        chatHistory = ChatHistory.query.get(user_id)
        if chatHistory:
            db.session.delete(chatHistory)
            db.session.commit()

        return chatHistory.serialize() if chatHistory else None
    