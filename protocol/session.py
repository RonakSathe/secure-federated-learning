from dataclasses import dataclass,field
from typing import Dict
import uuid
import time
from .state import ProtocolState

@dataclass
class ProtocolSession:

    session_id: str = field(
        default_factory=lambda: str(uuid.uuid4)
    )
    round_number : int = 0
    participants : Dict = field(default_factory=dict)
    state: ProtocolState = ProtocolState.CREATED
    created_at: float = field(default_factory=time.time)

    