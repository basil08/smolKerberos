# smolKerberos - Implementing KerberosV4 from scratch

## how to run

run resource server 
python resource_server.py resource1 11 5050

run auth server
python authentication_server.py auth 5000

(hoping that user and resource are already pre-populated)

make a request to auth to get access token /
then, make a request to resource server for resource /get_resource_file/:id

## version 1

In an open network environment, machines that provide services must be able to confirm the identities of people who request service. If I contact the mail server and ask for my mail, the service program must be able to verify that I am who I claim to be

# major issues
1. user experience - have to request new ticket from charon from every new service i use. reusability is still possible for the same service.
2. each time i request a new ticket, my password is sent over (possibly compromised) network in cleartext. not good!

# simplications made
1. There is no network identifier. This will be auto-assigned to each user client and used in the access token along with username and service_name.

Format of the access token
key:value,key:value,key:value,...

## References 

1. [Designing an Authentication System: A dialogue in four scenes](https://web.mit.edu/Kerberos/dialogue.html)
