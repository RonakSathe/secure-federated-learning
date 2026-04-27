import flwr as fl
print("\n\n ========Starting Federated Server. =====")
fl.server.start_server(
    server_address="0.0.0.0:8080",
    config=fl.server.ServerConfig(num_rounds=300),
)
