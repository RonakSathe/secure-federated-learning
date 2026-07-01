class Transport:

    @staticmethod
    def encode_bytes(data: bytes):
        return list(data)
    
    @staticmethod
    def decode_bytes(data):
        return bytes(data)