from dataclasses import dataclass,field
from typing import Dict
import uuid
import time
import secrets
from .state import ProtocolState

@dataclass
class ProtocolSession:

    session_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    session_salt: bytes = field(default_factory=lambda: secrets.token_bytes(32))

    round_number : int = 0
    participants : list[int] = field(default_factory=list)
    state: ProtocolState = ProtocolState.CREATED
    created_at: float = field(default_factory=time.time)

    #---------NEW ----------------
    public_keys: dict = field(default_factory=dict)
    peer_assignments: dict = field(default_factory=dict)
    mask_packets : dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    