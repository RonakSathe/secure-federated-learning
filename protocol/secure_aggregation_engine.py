from protocol.client_protocol import CLientProtocol
from protocol.masking_context import MaskingContext
from protocol.masking_engine import MaskingEngine
from protocol.transport import Transport
import numpy as np

class SecureAggregationEngine:
    def __init__(self,protocol:CLientProtocol):
        self.protocol = protocol
        self.masking_engine = MaskingEngine()

    """Returns masked parameter if protocol is readty, otw. original params."""
    def secure_upload(self,parameters,config):  

        #Generate public key
        public_key = self._generate_public_key()
        shared_secret = self._establish_shared_secret(config)
        print(f"\n CLIENT")
        print(f"My node: {config['protocol-my-node']}")
        print(f"Peer: {config.get('protocol-peer-node')}")

        if shared_secret is None:
            print("[SecureAggregation] Waiting for peer....")
            return parameters,public_key
        
        masked = self._mask_parameters(parameters=parameters,shared_secret=shared_secret,config=config)
        print("[SecureAggregation] Parameters masked successfully")
        return masked,public_key
  
    def _establish_shared_secret(self,config):
        peer_node = config.get("protocol-peer-node")
        peer_public_key = config.get("protocol-peer-public-key")

        if peer_node is None or peer_public_key is None:
            return None
        peer_public_key = Transport.decode_bytes(peer_public_key)

        self.protocol.receive_peer_public_key(peer_node=peer_node,public_key=peer_public_key)
        shared_secret =self.protocol.compute_shared_secret()
        
        print("="*60)
        print(f"[CLIENT] {self.protocol.partition_id}")
        print(f"Shared Secret; {shared_secret.hex()[:32]}...")
        print("="*60)
        return shared_secret

    # Generate masked model parameters
    def _mask_parameters(self,parameters,shared_secret,config):
        if shared_secret is None:
            print("[SecureAggregation] No SHared Secret")
            print("[SecureAggregation] Sending original Parameter")
            return parameters
        
        mask_context = MaskingContext(
            shared_secret=shared_secret,
            session_id=config["protocol-session-id"],
            round_number=config["server-round"],
            session_salt=Transport.decode_bytes(config["protocol-session-salt"]),
            my_node_id=config["protocol-my-node"],
            peer_node_id=config["protocol-peer-node"],
        )

        mask_results = self.masking_engine.mask_parameters(parameters=parameters,context=mask_context)
        print("\n =========MASKING ========")
        for result in mask_results:
            print(f"Layer: {result.layer_id}")
            print("Original: ", np.linalg.norm(result.original))
            print("Mask: ", np.linalg.norm(result.mask))
            print("Masked: ", np.linalg.norm(result.masked))
            print("="*40)
        return [result.masked for result in mask_results]
    
    def _generate_public_key(self):
        return Transport.encode_bytes(self.protocol.generate_public_key())

    def protocol_ready(self,config):
        return(
            config.get("protocol-peer-node") is not None
            and
            config.get("protocol-peer-public-key") is not None
        )
    