from flwr.serverapp.strategy import FedAvg
class DebugFedAvg(FedAvg):
    def aggregate_train(
            self,server_round,replies
    ):
        replies = list(replies)
        print("\n -=================ROund", server_round)

        for msg in replies:
            print("Node", msg.metadata.src_node_id)
            print("Keys", msg.content.keys())
            print(msg.content["metrics"])
        
        return super().aggregate_train(server_round=server_round,replies=replies)