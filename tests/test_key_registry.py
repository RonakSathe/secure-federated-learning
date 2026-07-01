from protocol.key_registry import KeyRegistry, PublicKeyPacket
from security.key_manager import KeyManager

registry = KeyRegistry()
session = "SESSION-001"

for node in range(3):
    km = KeyManager()
    packet = PublicKeyPacket(
        session_id= session,
        node_id= node,
        public_key= km.get_public_key_bytes()
    )
    registry.register_key(packet)
print("\n ===================Registry ==============")

for node, packet in registry.get_all().items():
    print(f"\nNode: {node} \nSession: {packet.session_id} \nKey: {packet.public_key.hex()[:32]}")