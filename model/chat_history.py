from app import db
from datetime import datetime

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    user_message = db.Column(db.Text, nullable = False)
    assistant_response = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.TIMESTAMP, nullable = True)

    #user = db.relationship('user', back_populates='chat_history', lazy=True)

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            #'user': self.user.serialize() if self.user else None,
            'user_message': self.user_message,
            'assistant_response': self.assistant_response,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deleted_at': self.deleted_at,
        }
