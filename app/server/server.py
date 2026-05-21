import csv
from pathlib import Path
import flwr as fl

#Logs folder + metrics file
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "metrics.csv"

#Custom FLower Strategy
class SaveMetricsStrategy(fl.server.strategy.FedAvg):
    
    def aggregate_fit(self, server_round, results, failures):
        aggregated = super().aggregate_fit(server_round, results, failures)
        attack_flag = 0
        update_magnitude = 0.0
        client_trust = 0.0

        if results:
            total_examples = 0
            weighted_attack = 0.0
            weighted_update = 0.0
            weighted_trust = 0.0
        
        for _,res in results:
            m = res.metrics or {}
            n = res.num_examples
            weighted_attack += n*float(m.get("attack_flag", 0.0))
            weighted_update += n*float(m.get("update_magnitude", 0.0))
            weighted_trust += n*float(m.get("client_trust", 0.0))
            total_examples += n
        if total_examples > 0:
            attack_flag = float(weighted_attack / total_examples)
            update_magnitude = weighted_update / total_examples
            client_trust = weighted_trust / total_examples
        self._last_fit_metrics = {
            "attack_flag": attack_flag,
            "update_magnitude": update_magnitude,
            "client_trust": client_trust,
        }
        return aggregated

    def aggregate_evaluate(self,server_round,results,failures):
        #FedAvg aggregate loss;  we compute accuracy ourselves
        aggregated = super().aggregate_evaluate(server_round, results, failures)
        loss_aggregated = 0.0
        accuracy_aggregated =  0.0

        if aggregated is not None:
            loss_aggregated,metrics_aggregated = aggregated
            accuracy_aggregated = float(metrics_aggregated.get("accuracy", 0.0))
        
        fit_metrics = getattr(self, "_last_fit_metrics", {})
        attack_flag = fit_metrics.get("attack_flag", 0.0)
        update_magnitude = fit_metrics.get("update_magnitude", 0.0)
        client_trust = fit_metrics.get("client_trust", 0.0)

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_exists = LOG_FILE.exists()
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["round", "loss", "accuracy", "update_magnitude", "attack_flag", "client_trust", "status"])
            status = "blocked" if attack_flag == 1 and client_trust < 0.5 else "accepted"
            writer.writerow([server_round,
                              loss_aggregated,
                                accuracy_aggregated,
                                  update_magnitude,
                                    attack_flag,
                                      client_trust,
                                        status])
            print(
                f"Round {server_round}: Loss = {loss_aggregated},"
                f"accuracy = {accuracy_aggregated}, trust={client_trust}"
            )
            return aggregated

def start_server():
    strategy = SaveMetricsStrategy()
    fl.server.start_server(server_address="0.0.0.0:8080",
                            config=fl.server.ServerConfig(num_rounds=10),
                            strategy=strategy
                            )
if __name__ == "__main__":    start_server()