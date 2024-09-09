from flask import Flask, jsonify, request

from models.models import db, Service, Resource
import logging
import argparse
import os
import json
import hashlib
import base64
# from utils import decrypt_data
from caesar import encrypt_data, decrypt_data

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", filename="master.log"
)

def pad_key_to_32_bytes(key):
    sha256 = hashlib.sha256()
    sha256.update(key.encode())
    # return sha256.digest()
    return base64.urlsafe_b64encode(sha256.digest()[:32])

class ResourceServer:
    def __init__(self, name: str, password: int, port: int):
        self.name = name
        self.password = password
        self.app = Flask(self.name)
        self.port = port

        basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'kerberos.db')
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)

        with self.app.app_context():
            db.create_all()

        # create a new entry in the service table
        self.service_init(self.name, self.password)
        self.setup_routes()

    def service_init(self, name, password):
        logging.info("Registering a new service: {}".format(name))
        with self.app.app_context():
            service = Service(service_name=name, service_password=password)
            self.id = service.id
            db.session.add(service)
            db.session.commit()
            logging.info("Service registered successfully")

    def parse_access_token(self, token):
        fields = token.split(",")
        # return { f.split(":") for f in fields }
        return { f.split(":")[0]: f.split(":")[1] for f in fields }
        
    def setup_routes(self):

        @self.app.before_request
        def service_init():
            db.create_all()

        @self.app.route("/get_service_name")
        def get_service_name():
            return jsonify({"service_name": self.name})

        @self.app.route("/get_resource_file/<int:resource_id>")
        def get_resource_file(resource_id):
            access_token = request.args.get("access_token")
            username = request.args.get("username")
            service_name = request.args.get("service_name")

            # pad_key = pad_key_to_32_bytes(self.password)
            # f = Fernet(pad_key)
            # decrypted_access_token = f.decrypt(access_token)
            # username, service_name = json.loads(decrypted_access_token.decode())

            decrypted_access_token = decrypt_data(access_token, self.password)
            #  = decrypted_access_token["username"], decrypted_access_token["service_name"]

            print("Username", username)
            print("Service name", service_name)

            print("Decrypted data", decrypted_access_token)

            decrypted_access_token = self.parse_access_token(decrypted_access_token)
            if decrypted_access_token['service_name'] != self.name:
                return jsonify({"error": "Invalid service name"})
            
            if service_name is None:    
                return jsonify({"error": "Service name is required"})
            
            if service_name != decrypted_access_token['service_name']:
                return jsonify({"error": "Invalid service name"})
            
            if username is None:
                return jsonify({"error": "Username is required"})
        
            if username != decrypted_access_token['username']:
                return jsonify({"error": "Invalid username"})
            
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

    def run(self, debug=True):
        self.app.run(debug=debug, port=self.port)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="Name of the service", required=True)
    parser.add_argument("--password", help="Password of the service", type=int, required=True)
    parser.add_argument("--port", help="Port number to run the service", required=True)
    args = parser.parse_args()
    try:
        app_instance = ResourceServer(args.name, args.password, args.port)
        app_instance.run()
    except Exception as e:
        logging.error("Error in running the service: {}".format(e))
        raise e