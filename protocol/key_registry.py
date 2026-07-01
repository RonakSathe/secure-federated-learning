from dataclasses import dataclass,field
import time
from .session import ProtocolSession
from .packets import PublicKeyPacket
#Responsibility  is to collect Public keys, store them and DIstribute them whever needed

class KeyRegistry:
    
    def register_key(self,session:ProtocolSession,packet:PublicKeyPacket):
        session.public_keys[packet.node_id] = packet
        print(f"Registered public key for node: {packet.node_id}")
    
    def contains(self,session,node_id):
        return node_id in session.public_keys
    
    def get_packet(self,session,node_id):
        return session.public_keys.get(node_id)
    
    
    def get_public_key(self,session:ProtocolSession,node_id:str):
        packet =self.get_packet(session,node_id)
        if packet is None:
            return None
        return packet.public_key
    
    def get_all_packets(self,session:ProtocolSession):
        return list(session.public_keys.values())
    
    def get_all_node_ids(self,session:ProtocolSession):
        return list(session.public_keys.keys())
    
    def clear(self,session):
        session.public_keys.clear()
        print("\nCleared all public keys from the registry.")

    def size(self,session):
        return len(session.public_keys)
    
    def is_complete(self,session):
        return len(session.public_keys) == len(session.participants)
    
    def print_registry(self,session:ProtocolSession):
        print("\n===================Key Registry=====================")
        for packet in session.public_keys.values():
            print(f"Node ID: {packet.node_id}, Public Key: {packet.public_key}")