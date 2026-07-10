from protocol.coordinator import ProtocolCoordinator
from protocol.message_builder import ProtocolMessageBuilder
from protocol.reply_processor import ReplyProcessor

class ServerProtocolEngine:
    def __init__(self):
        self.coordinator = ProtocolCoordinator()
        self.message_builder = ProtocolMessageBuilder()
        self.reply_processor = ReplyProcessor()
    def start_round(self,round_number,participants):

        session = self.coordinator.start_round(round_number=round_number,participants=participants)

        print("="*70)
        print("START ROUND")
        print("="*70)
        print(f"Round   : {round_number}")
        print(f"Participants: {len(participants)}")

        for p in participants:
            print(f"   {p}")

        print(f"Stored Public keys before round: {len(self.current_session.public_keys)}")
        print("="*70)
        return session

    @property
    def current_session(self):
        return self.coordinator.current_session
    
    @property
    def public_key_count(self):
        return len(self.current_session.public_keys)
    #PRepare one secure aggregation round
    def prepare_round(self,server_round,arrays,config,grid,strategy):
        pass

    #Processing Client replies
    # def process_train_replies(self,server_round,replies,strategy):
        # pass

    def build_training_messages(self,strategy,arrays,base_config,node_ids,server_round):
        return self.message_builder.build_train_messages(
            session=self.current_session,
            arrays=arrays,
            base_config=base_config,
            node_ids=node_ids,
            arrayrecord_key=strategy.arrayrecord_key,
            configrecord_key=strategy.configrecord_key,
            server_round=server_round,
        )
    
    def process_train_replies(self,replies,server_round):
        return self.reply_processor.process_train_replies(session=self.current_session,server_round=server_round,replies=replies,key_registry=self.coordinator.key_registry)