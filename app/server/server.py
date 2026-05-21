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
        if aggregated is not None:
            loss_aggregated,_ = aggregated
        
        total_examples = 0
        weighted_accuracy = 0.0

        for _,res in results:
            acc = float(res.metrics.get("accuracy",0.0))
            weighted_accuracy += res.num_examples * acc
            total_examples += res.num_examples
        
        accuracy_aggregated = (
            weighted_accuracy/total_examples if total_examples > 0 else 0.0
        )
        fit_metrics = getattr(self,"_last_fit_metrics",{})
        attack_flag = fit_metrics.get("attack_flag",0.0)
        update_magnitude = fit_metrics.get("update_magnitude",0.0)
        client_trust = fit_metrics.get("client_trust",0.0)

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_exists = LOG_FILE.exists()
        with open(LOG_FILE,"a",newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["round",
                                 "loss",
                                 "accuracy",
                                 "update_magnitude",
                                 "attack_flag",
                                 "client_trust",
                                 "status",
                                ])
            status = "OK"
            if attack_flag > 0.5:
                status = "Attack Detected"
            elif client_trust < 0.25:
                status = "Low Trust Client"
            writer.writerow([server_round, loss_aggregated, accuracy_aggregated, update_magnitude, attack_flag, client_trust, status])

        writer.writerow([
            server_round,
            loss_aggregated,
            accuracy_aggregated,
            update_magnitude,
            attack_flag,
            client_trust,
            status
        ])

        print(f"\n\nRound: {server_round} - Loss: {loss_aggregated:.4f}, Accuracy: {accuracy_aggregated:.2%}, Update Mag: {update_magnitude:.4f}, Attack Flag: {attack_flag:.2f}, Client Trust: {client_trust:.2f}, Status: {status}")
        return aggregated

def start_server():
    strategy = SaveMetricsStrategy()
    fl.server.start_server(server_address="0.0.0.0:8080",
                            config=fl.server.ServerConfig(num_rounds=20),
                            strategy=strategy
                            )
if __name__ == "__main__":    start_server()