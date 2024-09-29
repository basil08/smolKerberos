# smolKerberos - Implementing KerberosV4 from scratch

## metadata

* New resource created response from auth server 

{
    "data": {
        "data": "if you're seeing this, then you got the resource yay!",
        "description": "resource1",
        "id": 1,
        "name": "resource1"
    },
    "status": "Resource added successfully"
}

* New user created response from auth server

{
    "data": {
        "id": 1,
        "name": "basil"
    },
    "status": "User added successfully"
}



## how to run

run resource server 
python resource_server.py resource1 11 5050

run auth server
python authentication_server.py auth 5000

(hoping that user and resource are already pre-populated)

make a request to auth to get access token /
then, make a request to resource server for resource /get_resource_file/:id

## version 2

>  inventing a new network service. It's called the "ticket-granting" service, a service that issues Charon tickets to users who have already proven their identity to Charon. You can use this ticket-granting service if you have a ticket for it, a ticket-granting ticket.

The ticket-granting service is really just a version of Charon in as much as it has access to the Charon database. It's a part of Charon that lets you authenticate yourself with a ticket instead of a password.

Anyhow, the authentication system now works as follows: you login to a workstation and use a program called kinit to contact the Charon server. You prove your identity to Charon, and the kinit program gets you a ticket-granting ticket.

Now say you want to get your mail from the mail server. You don't have a mail server ticket yet, so you use the "ticket-granting" ticket to get the mail server ticket for you. You don't have to use your password to get the new ticket.

> Once you have acquired a ticket-granting ticket, you don't need to get another. You use the ticket-granting ticket to get the other tickets you need.

---

> Charon uses the username to look up your password. Next Charon builds a packet of data that contains the ticket-granting ticket. Before it sends you the packet, Charon uses your password to encrypt the packet's contents.

Your workstation receives the ticket packet. You enter your password. Kinit attempts to decrypt the ticket with the password you entered. If kinit succeeds, you have successfully authenticated yourself to Charon.

---

Tokens still prone to REPLAY attacks as service tokens are not expirable

> make all tokens, access and service tokens to be expirable 

> there's still the issue of REPLAY attacks before the expiration if an adversary gets access to the tokens before the expiration.

Client workflow for version 2
![alt text](image.png)


## version 1

In an open network environment, machines that provide services must be able to confirm the identities of people who request service. If I contact the mail server and ask for my mail, the service program must be able to verify that I am who I claim to be

# major issues
1. user experience - have to request new ticket from charon from every new service i use. reusability is still possible for the same service.
2. each time i request a new ticket, my password is sent over (possibly compromised) network in cleartext. not good!

# simplications made
1. ~~There is no network identifier. This will be auto-assigned to each user client and used in the access token along with username and service_name.~~ Added a barebone client program which randomly generates a client_id to simulate the idea of an immutable network identifier.
2. The password is an int (for sake of this demo)
3. Ideally, the stesp to get auth token and then service access token for any service will be abstracted away / hidden from the user but for simplicity (and understanding), those are made explicit in the client program.
4. Leaving testing the token expire workflow. Ideally, the client should be smart enough to detect a token expired exception and reinitiate a fresh request to the auth and service token grantor servers.


Format of the access token
key:value,key:value,key:value,...


## Further improvements 

1. Re-issue token service
2. Authorization layer on top of authentication layer


## References 

1. [Designing an Authentication System: A dialogue in four scenes](https://web.mit.edu/Kerberos/dialogue.html)
