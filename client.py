import argparse
import requests
import random

from caesar import decrypt_data, encrypt_data

def get_auth_packet(username, auth_server, client_id):
    """
    Get the auth token from the auth server

    """
    # create a dictionary with the username
    data = {"username": username, "client_id": client_id}
    # make a POST request to the auth server to get the auth token
    response = requests.get(f"{auth_server}/get_auth_token", params=data)
    # if the response is not successful, return None
    if response.status_code != 200:
        return None
    # get the auth token from the response
    auth_packet = response.json().get("auth_packet")
    # return the auth token
    return auth_packet

def get_service_packet(username, auth_token, resource_serv_name, sgt_server_url, client_id, authenticator):
    # create a dictionary with the username and password

    # authenticator = decrypt_data(auth_token, int(password))

    
    data = {
        "username": username,
        "service_name": resource_serv_name,
        "client_id": client_id,
        "auth_token": auth_token,
        "authenticator": authenticator
    }

    print("Debug data", data)
    # make a POST request to the auth server to get the access token
    # response = requests.get(f"{auth_server}/get_access_token", json=data)

    # make a GET request to the auth server to get the access token
    response = requests.get(f"{sgt_server_url}/get_service_token", params=data)
    # if the response is not successful, return None
    if response.status_code != 200:
        print("response error", response.json())
        # print("response.error", response.error)
        return None
    # get the access token from the response
    res_data = response.json()
    print("Debug response", res_data)
    service_packet = res_data.get("service_packet")
    # return the access token

    return service_packet
    

def main(args):
    username = args.username
    client_id = random.randint(10000, 1000000)
    commands = ["gat (get auth token)", "get (get resource)", "gst (get service token)", "exit"]
    # get the auth server URL
    auth_server = args.auth
    # auth_server = args.get("auth_server")
    # auth_server = args['auth_server']
    if not auth_server:
        auth_server = "http://localhost:5000"
        print("[+] Using default auth server URL:", auth_server)

    sgt_server_url = args.sgt

    if not sgt_server_url:
        sgt_server_url = "http://localhost:5025"
        print("[+] Using default service token grantor URL:", sgt_server_url)

    resource_server = args.resource
    
    if not resource_server:
        resource_server = "http://localhost:5050"
        print("[+] Using default resource server URL:", resource_server)
    
    auth_session_key = None
    service_session_key = None

    while True:
        # get the message from the user
        message = input("> ")
        # create a dictionary with the message
        # data = {"message": message}
        tokens = message.split()
        try:
            command = tokens[0]
            params = tokens[1:]
        except IndexError:
            continue
        except UnboundLocalError:
            continue
        
        if command == "gat":
            auth_packet = get_auth_packet(username, auth_server, client_id)

            if auth_packet is None:
                print("Cannot get auth packet. Please check your username. Maybe the auth server is down or contact your network admin")
                continue

            password = input("Enter password: ")

            if not password:
                print("You must enter a password to run 'gat' commands")
                continue
            
            # decrypt the auth token using user password
            data = decrypt_data(auth_packet, int(password))
            fields = data.split("|")
            parsed_packet = { f.split(":")[0]: f.split(":")[1] for f in fields }
            auth_token = parsed_packet.get("auth_token")

            print("auth token")
            print(auth_token)
            auth_session_key = parsed_packet.get("auth_session_key")
            print("auth session key")
            print(auth_session_key)

            decrypted_token = decrypt_data(auth_token, int(password))
            print("decrypted token")
            print(decrypted_token)

        elif command == 'gst':
            print("Getting service token")
            try:
                resource_serv_name = params[0]
                # resource_id = params[1]
                client_id = params[1]
                auth_token = params[2]
            except IndexError:
                print("Usage: gst: gst <resource server name> <client id> <auth token>")
                continue
            
            if auth_session_key is None:
                print("No auth_session_key set. You must run 'gat' command first before running 'gst' command")
                continue

            authenticator = {
                "username": username,
                "client_id": client_id,
            }

            # parse authenticator into a string
            authenticator = ",".join([f"{k}:{v}" for k, v in authenticator.items()])

            authenticator = encrypt_data(authenticator, int(auth_session_key))

            

            service_token = get_service_packet(username, auth_token, resource_serv_name, sgt_server_url, client_id, authenticator)
            if service_token is None:
                print("Cannot get service token. Please check your username. Maybe the auth server is down or contact your network admin")
                continue
            # if service_token.get("error"):
            #     print("Error:", service_token.get("error"))
            #     continue
            print("Service token")
            print(service_token)

            decrypted_service_token = decrypt_data(service_token, int(auth_session_key))
            print("Decrypted service token")
            print(decrypted_service_token)

            # parse decrypted session token into a dict
            fields = decrypted_service_token.split("|")
            parsed_service_token = { f.split(":")[0]: f.split(":")[1] for f in fields }
            service_session_key = parsed_service_token.get("service_session_key")
            service_token = parsed_service_token.get("service_token")
            print("Service session key")
            print(service_session_key)
            print("Service token")
            print(service_token)
        elif command == "exit":
            print("Exiting client")
            break
        elif command == "get":
            print("Getting resource")
            try:
                resource_serv_name = params[0]
                resource_id = params[1]
                access_token = params[2]
            except IndexError:
                print("Usage: get: get <resource server name> <resource id>  <access token>")
                continue
            except UnboundLocalError:
                print("Usage: get: get <resource server name> <resource id> <access token>")
                continue

            authenticator = {
                "username": username,
                "client_id": client_id,
            }

            if service_session_key is None:
                print("No service_session_key set. You must run 'gst' command first before running 'get' command")
                continue

            # parse authenticator into a string
            authenticator = ",".join([f"{k}:{v}" for k, v in authenticator.items()])
            authenticator = encrypt_data(authenticator, int(service_session_key))

            data = {
                "access_token": access_token,
                "username": username,
                "service_name": resource_serv_name,
                "resource_id": resource_id,
                "client_id": client_id,
                "authenticator": authenticator
            }


            print("Debug pinging ", f"{resource_server}/get_resource_file/{resource_id}")
            response = requests.get(f"{resource_server}/get_resource_file/{resource_id}", params=data)

            if response.status_code != 200:
                print("error", response)
                # return { 'error': response }
                continue
            
            print(response.json())
        else:
            print("Unknown command. You can use any of ", ",".join(commands))

if __name__ == "__main__":
    # use argparse to parse the command line arguments
    parser = argparse.ArgumentParser(description="Client program")
    parser.add_argument("--username", help="Username of the client", required=True)
    parser.add_argument("--auth", help="Auth server URL", required=False)
    parser.add_argument("--resource", help="Resource server URL", required=False)
    parser.add_argument("--sgt", help="Service token grantor URL", required=False)

    # generate a random number between 10000 and 1000000

    # parser.add_argument("port", help="Server port")
    args = parser.parse_args()
    main(args)
