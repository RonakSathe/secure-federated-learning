import csv
from pathlib import Path
import flwr as fl

#Logs folder + metrics file
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "metrics.csv"

#Custom FLower Strategy
class SaveMetricsStrategy(fl.server.strategy.FedAvg):
    def aggregate_evaluate(self,server_round,results,failures):
        #FedAvg aggregate loss;  we compute accuracy ourselves
        loss_aggregated,_ = super().aggregate_evaluate(server_round, results, failures)
        
        if not results:
            return loss_aggregated, {"accuracy":0}
        
        total_examples = 0
        weighted_accuracy = 0.0
        
        for _, res in results:
            acc = res.metrics.get("accuracy", 0.0)
            weighted_accuracy += res.num_examples*float(acc)
            total_examples += res.num_examples
        
        accuracy_aggregated = weighted_accuracy / total_examples if total_examples else 0.0
            
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_exists = LOG_FILE.exists()

        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            #Write header once
            if not file_exists:
                writer.writerow(["round", "loss", "accuracy"])
            writer.writerow([server_round, f"{loss_aggregated:.4f}" or "0.0000", f"{accuracy_aggregated:.4f}"])

        print(f"Round {server_round} - Loss: {loss_aggregated:.4f}, Accuracy: {accuracy_aggregated:.4f}")    
        return loss_aggregated, {"accuracy": accuracy_aggregated}
    
    

def start_server():
    strategy = SaveMetricsStrategy()
    fl.server.start_server(server_address="0.0.0.0:8080",
                            config=fl.server.ServerConfig(num_rounds=10),
                            strategy=strategy
                            )
if __name__ == "__main__":    start_server()