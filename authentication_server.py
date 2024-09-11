from flask import Flask, jsonify, request

from models.models import db, Service, Resource, User
import logging
import argparse
import os

# from utils import encrypt_data
from caesar import encrypt_data

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", filename="master.log"
)

class AuthenticationServer:
    def __init__(self, name, port):
        self.name = name
        self.app = Flask(self.name)
        self.port = port

        basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'kerberos.db')
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)

        with self.app.app_context():
            db.create_all()

        # create a new entry in the service table
        # self.service_init(self.name, self.password)
        self.setup_routes()

    def setup_routes(self):

        @self.app.before_request
        def service_init():
            db.create_all()

        @self.app.route("/get_access")
        def get_access():
            return jsonify({"status": "Access granted"})
        
        @self.app.route("/get_access_token")
        def get_access_token():
            username = request.args.get('username')
            service_name = request.args.get('service_name')
            password = request.args.get('password')
            client_id = request.args.get('client_id')

            print("Debugging username", username)
            print("Debugging service_name", service_name)
            print("Debugging password", password)
            print("Debugging client id", client_id)

            user = User.query.filter_by(username=username).first()
            if user is None:
                return jsonify({"error": "User not found"})
            password = int(password)
            ## ideally this should be hashed but this is a educational project
            if user.password != password:
                return jsonify({"error": "Invalid password"})

            if service_name is None:
                return jsonify({"error": "Service name is required"})
            service = Service.query.filter_by(service_name=service_name).first()
            if service is None:
                return jsonify({"error": "Service not found"})
            
            print("service password", service.service_password)

            # payload = { 'username': username, 'service_name': service_name }
            payload = ",".join(["username:" + username, "service_name:" + service_name, "client_id:" + client_id])
            token = encrypt_data(payload, service.service_password)
            # print("token", token)
            return jsonify({"access_token": str(token) })

        @self.app.route("/get_service_name")
        def get_service_name():
            return jsonify({"service_name": self.name})

        # DEBUG functions 

        @self.app.route("/get_resource_file/<int:resource_id>")
        def get_resource_file(resource_id):
            resource = Resource.query.filter_by(id=resource_id).first()
            if resource is None:
                return jsonify({"error": "Resource not found"})
            return jsonify(resource.to_dict())

        @self.app.route("/set_resource_file", methods=["POST"])
        def set_resource_file():
            if request.content_type == "application/json":
                resource_name = request.json.get("name")
                resource_description = request.json.get("description")
                resource_data = request.json.get("data")
            elif request.content_type == "application/x-www-form-urlencoded":
                resource_name = request.form.get("name")
                resource_description = request.form.get("description")
                resource_data = request.form.get("data")
            resource = Resource(
                resource_name=resource_name,
                resource_description=resource_description,
                resource_data=resource_data,
            )
            db.session.add(resource)
            db.session.commit()
            return jsonify({"status": "Resource added successfully", "data": resource.to_dict()})

        @self.app.route("/set_user", methods=["POST"]) 
        def set_user():
            if request.content_type == "application/json":
                username = request.json.get("username")
                password = request.json.get("password")
            elif request.content_type == "application/x-www-form-urlencoded":
                username = request.form.get("username")
                password = request.form.get("password")
            user = User(
                username=username,
                password=password,
            )
            db.session.add(user)
            db.session.commit()
            return jsonify({"status": "User added successfully", "data": user.to_dict()})
        
        @self.app.route("/get_user")
        def get_user():
            username = request.args.get("username")
            user = User.query.filter_by(username=username).first()
            if user is None:
                return jsonify({"error": "User not found"})
            return jsonify(user.to_dict())
        
        @self.app.route("/delete_user")
        def delete_user():
            username = request.args.get("username")
            user = User.query.filter_by(username=username).first()
            if user is None:
                return jsonify({"error": "User not found"})
            db.session.delete(user)
            db.session.commit()
            return jsonify({"status": "User deleted successfully", "data": user.to_dict()})
    def run(self, debug=True):
        self.app.run(debug=debug, port=self.port)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="Name of the service", required=True)
    parser.add_argument("--port", help="Port number to run the service", required=True)
    args = parser.parse_args()

    try:
        app_instance = AuthenticationServer(args.name, args.port)
        app_instance.run()
    except Exception as e:
        logging.error("Error in running the service: {}".format(e))
        raise e