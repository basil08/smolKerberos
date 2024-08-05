# smolKerberos - Implementing KerberosV4 from scratch

Some notes:

1. This implementation, rather naively, uses a common database which it shares across all components of the system. This has been done for brevity and to not worry about propagating database changes (especially from user and service tables) to every component in the network. 
2. The passwords are stored in cleartext as this is an educational implementation. In a production implemention, this will OBVIOUSLY not be the case.

## References 

1. [Designing an Authentication System: A dialogue in four scenes](https://web.mit.edu/Kerberos/dialogue.html)
