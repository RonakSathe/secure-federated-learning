from dataclasses import dataclass

@dataclass
class MaskContext:
    session_id: str
    round_number : int
    layer_id: int
    salt: bytes