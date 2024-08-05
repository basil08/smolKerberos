from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.username,
        }

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servicename = db.Column(db.String(80), unique=True, nullable=False)
    service_password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<Service {self.servicename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.servicename,
        }