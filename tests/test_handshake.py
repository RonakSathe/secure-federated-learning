from protocol.client_protocol import CLientProtocol

#Create two clients
client1 = CLientProtocol(partition_id=1)
client2 = CLientProtocol(partition_id=2)

#Generwte public keys
pk1 = client1.generate_public_key()
pk2 = client2.generate_public_key()


#Simulte Peerpacket delivery
client1.receive_peer_public_key(peer_node=2,public_key=pk2)
client2.receive_peer_public_key(peer_node=1,public_key=pk1)

#COmpute Secrets
secret1  = client1.print_shared_secret()
secret2 = client2.print_shared_secret()

print("Secrets Equal: ?", secret1==secret2)