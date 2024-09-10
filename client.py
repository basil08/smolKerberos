import json
import argparse
import requests
import random

def get_access_token(username, password, resource_serv_name, resource_id, auth_server, client_id):
    # create a dictionary with the username and password
    data = {
        "username": username,
        "password": password,
        "service_name": resource_serv_name,
        "client_id": client_id
    }

    print("Debug data", data)
    # make a POST request to the auth server to get the access token
    # response = requests.get(f"{auth_server}/get_access_token", json=data)

    # make a GET request to the auth server to get the access token
    response = requests.get(f"{auth_server}/get_access_token", params=data)
    # if the response is not successful, return None
    if response.status_code != 200:
        print("response.error", response.error)
        return None
    # get the access token from the response
    res_data = response.json()
    print("Debug response", res_data)
    access_token = res_data.get("access_token")
    # return the access token
    return access_token
    

def main(args):
    username = args.username
    client_id = random.randint(10000, 1000000)
    commands = ["gat", "get", "exit"]
    # get the auth server URL
    auth_server = args.auth
    # auth_server = args.get("auth_server")
    # auth_server = args['auth_server']
    if not auth_server:
        auth_server = "http://localhost:5000"
        print("[+] Using default auth server URL:", auth_server)
    # get the resource server URL
    resource_server = args.resource
    # resource_server = args.get("resource_server")
    # resource_server = args['resource_server']
    if not resource_server:
        resource_server = "http://localhost:5050"
        print("[+] Using default resource server URL:", resource_server)

    while True:
        # get the message from the user
        message = input("> ")
        # create a dictionary with the message
        # data = {"message": message}
        tokens = message.split()
        command = tokens[0]
        params = tokens[1:]
        
        if command == "gat":
            resource_serv_name = params[0]
            resource_id = params[1]
            password = input("Enter password: ")

            if not password:
                print("You must enter a password to run 'gat' commands")
                continue

            access_token = get_access_token(username, password, resource_serv_name, resource_id, auth_server, client_id)

            if access_token is None:
                print("Cannot get access token. Maybe the auth server is down. Otherwise check your password")
                continue

            print(access_token)
        elif command == "exit":
            print("Exiting client")
            break
        elif command == "get":
            print("Getting resource")
            access_token = params[0]
            resource_serv_name = params[1]
            resource_id = params[2]
            data = {
                "access_token": access_token,
                "username": username,
                "service_name": resource_serv_name,
                "resource_id": resource_id,
                "client_id": client_id
            }
            print("Debug pinging ", f"{resource_server}/get_resource_file/{resource_id}")
            response = requests.get(f"{resource_server}/get_resource_file/{resource_id}", params=data)

            if response.status_code != 200:
                return { 'error': response.error }
            
            print(response.json())
        else:
            print("Unknown command. You can use any of ", ",".join(commands))

if __name__ == "__main__":
    # use argparse to parse the command line arguments
    parser = argparse.ArgumentParser(description="Client program")
    parser.add_argument("--username", help="Username of the client", required=True)
    parser.add_argument("--auth", help="Auth server URL", required=False)
    parser.add_argument("--resource", help="Resource server URL", required=False)

    # generate a random number between 10000 and 1000000

    # parser.add_argument("port", help="Server port")
    args = parser.parse_args()
    main(args)
