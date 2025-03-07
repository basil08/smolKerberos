import random
from flask import Flask, jsonify, request

from models.models import db, Service, Resource, User
import logging
import argparse
import os
import json
import time

# from utils import encrypt_data
from caesar import encrypt_data, decrypt_data

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", filename="master.log"
)


def parse_decrypted_token(token):
    fields = token.split(",")
    return {f.split(":")[0]: f.split(":")[1] for f in fields}


class ServiceTokenGrantor:
    def __init__(self, name, port):
        self.name = name
        self.app = Flask(self.name)
        self.port = port

        with open("config.json", "r") as f:
            config = json.load(f)
            self.password = config.get("service_token_grantor_password")
            self.lifespan = config.get("lifespan")

        basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
            basedir, "kerberos.db"
        )
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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

        @self.app.route("/get_service_token")
        def get_service_token():
            username = request.args.get("username")
            service_name = request.args.get("service_name")
            client_id = request.args.get("client_id")
            auth_token = request.args.get("auth_token")
            authenticator = request.args.get("authenticator")

            print("Debugging username", username)
            print("Debugging service_name", service_name)
            print("Debugging client id", client_id)
            print("Debugging auth token", auth_token)

            user = User.query.filter_by(username=username).first()
            if user is None:
                return jsonify({"error": "User not found"})
            # password = int(password)
            ## ideally this should be hashed but this is a educational project
            # if user.password != password:
            #     return jsonify({"error": "Invalid password"})

            # try to decrypt the auth token and match the service_token_grantor_password with own password (so we know that this auth token came from the auth server)
            try:
                decrypted_token = decrypt_data(auth_token, user.password)
                print("Decrypted token", decrypted_token)
            except Exception as e:
                print("Unable to decrypt auth token", e)
                return jsonify({"error": "Unable to decrypt auth token"})

            payload = parse_decrypted_token(decrypted_token)
            print("Payload", payload)

            if service_name is None:
                return jsonify({"error": "Service name is required"})
            
            service = Service.query.filter_by(service_name=service_name).first()
            if service is None:
                return jsonify({"error": "Service not found"})
            # print("service password", service.service_password)

            if username is None:
                return jsonify({"error": "Username is required"})

            if client_id is None:
                return jsonify({"error": "Client ID is required"})

            if username != payload.get("username"):
                return jsonify(
                    {
                        "error": "Invalid username. Mismatch between username in packet and decrypted username."
                    }
                )

            if client_id != payload.get("client_id"):
                return jsonify(
                    {
                        "error": "Invalid client ID. Mismatch between client ID in packet and decrypted"
                    }
                )

            # get current time in seconds since epoch
            current_timestamp_in_seconds_since_epoch = str(int(time.time()))
            # check if token is valid
            if int(current_timestamp_in_seconds_since_epoch) - int(
                payload.get("timestamp")
            ) > int(payload.get("lifespan")):
                return jsonify({"error": "Auth token expired. Please reauthenticate"})

            # check if the token is actually sent by the toker's owner or not
            if authenticator is None:
                return jsonify({"error": "Authenticator is required"})
            
            decrypted_authenticator = decrypt_data(authenticator, int(payload.get("auth_session_key")))

            if decrypted_authenticator is None:
                return jsonify({"error": "Invalid authenticator"})

            print("decrypted authenticator", decrypted_authenticator)

            # parse the authenticator into a python dict
            authenticator_fields = decrypted_authenticator.split(",")
            authenticator_dict = {f.split(":")[0]: f.split(":")[1] for f in authenticator_fields}

            if authenticator_dict.get("username") != username:
                return jsonify({"error": "Username in authenticator and username does not match"})

            if authenticator_dict.get("client_id") != client_id:
                return jsonify({"error": "Client ID in authenticator and client ID does not match"})
            
            if authenticator_dict.get("username") != payload.get("username"):
                return jsonify({"error": "Username in authenticator and username in token does not match"})
            
            if authenticator_dict.get("client_id") != payload.get("client_id"):
                return jsonify({"error": "Client ID in authenticator and client ID in token does not match"})
            
            # payload = { 'username': username, 'service_name': service_name }

            service_session_key = random.randint(10000, 1000000)

            service_token = ",".join(
                [
                    "username:" + username,
                    "service_name:" + service_name,
                    "client_id:" + client_id,
                    "timestamp:" + str(current_timestamp_in_seconds_since_epoch),
                    "lifespan:" + str(self.lifespan),
                    "service_session_key:" + str(service_session_key),
                ]
            )
            encrypted_service_token = encrypt_data(service_token, service.service_password)
            service_packet = "|".join(
                [
                    "service_token:" + encrypted_service_token,
                    "service_session_key:" + str(service_session_key),
                ]
            )

            print("Debug service packet", service_packet)
            encrypted_service_packet = encrypt_data(service_packet, int(payload.get("auth_session_key")))
            print("Debug encrypted service packet", encrypted_service_packet)

            return jsonify({"service_packet": encrypted_service_packet})

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
            return jsonify(
                {"status": "Resource added successfully", "data": resource.to_dict()}
            )

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
            return jsonify(
                {"status": "User added successfully", "data": user.to_dict()}
            )

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
            return jsonify(
                {"status": "User deleted successfully", "data": user.to_dict()}
            )

    def run(self, debug=True):
        self.app.run(debug=debug, port=self.port)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="Name of the service", required=True)
    parser.add_argument("--port", help="Port number to run the service", required=True)
    args = parser.parse_args()

    try:
        app_instance = ServiceTokenGrantor(args.name, args.port)
        app_instance.run()
    except Exception as e:
        logging.error("Error in running the service: {}".format(e))
        raise e
