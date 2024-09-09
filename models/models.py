from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.username,
        }

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_name = db.Column(db.String(80), nullable=False)
    service_password = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Service {self.servicename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.servicename,
        }


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resource_name = db.Column(db.String(80), nullable=False)
    resource_description = db.Column(db.String(80), nullable=False)
    resource_data = db.Column(db.String(80), nullable=False)

    def __repr__(self) -> str:
        # return super().__repr__()
        return f'<Resource {self.resource_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.resource_name,
            'description': self.resource_description,
            'data': self.resource_data
        }