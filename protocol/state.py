from enum import Enum

class ProtocolState(Enum):
    CREATED = "created"
    KEY_EXCHANGE = "key_exchange"
    PARTICIPANTS_SELECTED = "PARTICIPANTS_SELECTED"
    PUBLIC_KEYS_REQUESTED = "PUBLIC_KEYS_REQUESTED"
    PUBLIC_KEYS_RECEIVED = "PUBLIC_KEYS_RECEIVED"
    MASK_GENERATED = "mask_generated"
    TRAINING = "training"
    MASK_UPLOAD = "mask_upload"
    AGGREGATION = "aggregation"
    COMPLETED = "completed"

    