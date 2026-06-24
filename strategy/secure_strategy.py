import json
from pathlib import Path
from flwr.serverapp.strategy import FedAvg

class SecureFedAvg(FedAvg):
    def aggregate_train(self,server_round,replies):
        valid_replies, failures = self._check_and_log_replies(replies,is_train=True)

        blocked_file = Path("dashboard/blocked_clients.json")
        blocked_clients = set()
        try:
            if blocked_file.exists():
                with open(blocked_file) as f:
                    data = json.load(f)
                blocked_clients = {
                    int(x["partition_id"]) for x in data.get("blocked_clients",[])
                }

                print("Blocked_CLients",blocked_clients)

        except Exception as e:
            print(f"Blocked File Error: {e}")

        print(f"\n Blocked CLients:  {blocked_clients}")

        filtered_replies = []

        for msg in valid_replies:
            metrics = msg.content["metrics"]
            pid = int(metrics["partition_id"])

            if pid in blocked_clients:
                print(f" Blocking CLient with the id: {pid}")
                continue
            filtered_replies.append(msg)
        
        print(f"Accepted  "
              f"{len(filtered_replies)} / "
              f"{len(valid_replies)} clients "
              )
        
        if len(filtered_replies) == 0:
            print("Warning: All clients blocked")
            return None,None
        
        return super().aggregate_train(server_round=server_round,replies=filtered_replies)