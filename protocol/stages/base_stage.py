from abc import ABC, abstractmethod
from protocol.session import ProtocolSession

class ProtocolStage(ABC):

    @abstractmethod
    def run(self,session:ProtocolSession):
        pass