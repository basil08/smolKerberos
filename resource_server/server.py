from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user import User, Service, db

class ResourceServer:
    def __init__(self, name, password, id, port=5001):
        self.app = Flask(name)
        self.name = name
        self.password = password
        self.id = id
        self.port = port
        self.setup_routes()

        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, '..', 'db', 'kerberos.db')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize the database
        db.init_app(self.app)

    def setup_routes(self):

        @self.app.before_request
        def create_tables():
            db.create_all()
        
        # @self.app.route("/get_grant_token")
        # def get_grant_token():


        @self.app.route("/create_user", methods=['POST'])
        def create_user():
            data = request.json
            username = data.get('username')
            password = data.get('password')
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return jsonify({
                "message": "User created successfully"
            })

        @self.app.route("/get_users")
        def get_users():
            users = User.query.all()
            users = [user.to_dict() for user in users]
            return jsonify(users)
        
        @self.app.route("/get_user/<int:id>")
        def get_user(id):
            user = User.query.filter_by(id=id).first()
            return jsonify(user.to_dict())
        
        @self.app.route("/create_service", methods=['POST'])
        def create_service():
            data = request.json
            servicename = data.get('servicename')
            service_password = data.get('service_password')
            service = Service(servicename=servicename, service_password=service_password)
            db.session.add(service)
            db.session.commit()
            return jsonify({
                "message": "Service created successfully"
            })

        @self.app.route("/get_services")
        def get_services():
            services = Service.query.all()
            services = [service.to_dict() for service in services]
            return jsonify(services)

    def run(self, debug=True):
        try:
            self.app.run(debug=debug, port=self.port)
        except Exception as e:
            print("Port {port} is busy. Please try another port.".format(port=self.port))
            print(e)

if __name__ == '__main__':
    resource_server = ResourceServer("service 1", "service pass 1", 1, 5050)
    resource_server.run()
