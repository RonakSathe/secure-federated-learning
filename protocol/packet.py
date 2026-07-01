from dataclasses import dataclass

@dataclass
class MaskPacket:
    node_id: int
    mask: int
    encrypted: bool = False
    salt: str = ""
    encrypted_mask: bytes | None = None
    session_id: str = ""
    