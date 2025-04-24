from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable = False)
    lastname = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), unique=True, nullable = False)
    password = db.Column(db.String(255), nullable = False)
    phone = db.Column(db.String(50),nullable = True)
    photo = db.Column(db.String(255), nullable = True)  
    status = db.Column(db.Boolean, server_default = '1')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.TIMESTAMP, nullable = True)

    #chat_history = db.relationship('chat_history', back_populates='user', lazy=True)


    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'email': self.email,
            'password':self.password,
            'phone': self.phone,
            'photo':self.photo,
            'status':self.status,
            #'chat_history': self.chat_history.serialize() if self.chat_history else None,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deleted_at': self.deleted_at,
        }
