from flwr.clientapp import ClientApp
import numpy as np
from flwr.app import (
    Message,
    Context,
    RecordDict,ArrayRecord,MetricRecord,
)
from .task import *
from .logger import log_client_metric
from .dataset_logger import save_training_sample
import time
from .attack import apply_attack
import random
# =========================================================================
from protocol.client_protocol import CLientProtocol
from protocol.transport import Transport

#Trainig data

app = ClientApp()


@app.train()
def train(msg:Message,context:Context):
    model = build_model()
    arrays = msg.content["arrays"]
    paramters = arrays.to_numpy_ndarrays()
    set_parameters(model, paramters)
    partition_id = context.node_config["partition-id"]

    # CLIENT PROTOCOL PART
    protocol = CLientProtocol(partition_id=partition_id)
    public_key = Transport.encode_bytes(protocol.generate_public_key())

    #Creating the record for the public key and adding it to the Metrics so that it could be sent to the server
    
    #====================================================
    # GET CURRENT ROUND
    #====================================================
    server_round = msg.content["config"]["server-round"]
    config = msg.content["config"]
    session_id = config["protocol-session-id"]
    session_salt = Transport.decode_bytes(config["protocol-session-salt"])
    peer_node = config.get("protocol-peer-node")
    peer_public_key = config.get("protocol-peer-public-key")

    if peer_node is not None and peer_public_key is not None:
        peer_public_key = Transport.decode_bytes(peer_public_key)
        protocol.receive_peer_public_key(peer_node=peer_node,public_key=peer_public_key)
        shared_secret = protocol.compute_shared_secret()
        print("="*50)
        print(f"[Client {partition_id}] Shared Secret: {shared_secret.hex()[:32]}...")
        print("="*50)
    else:
        print("[Client] waiting for peer information")

    print("\n==============PROTOCOL CONFIG ====================")

    print("Partition: ",partition_id)
    print("Sesion Id:", session_id)
    print("ROund: ",server_round)
    print("Salt: ",session_salt.hex()[:32],"...")
    print("\nxxxxxxxxxxxxxxxxEND CONFIG xxxxxxxxxxxxxxxxxxxxxx")


    random.seed(server_round)
    
    df = collect_batch(partition_id=partition_id)

    #Computing Averages for further utilization for securtiy analysis
    avg_cpu = df["cpu"].mean()
    avg_memory = df["memory"].mean()
    avg_connections = df["connections"].mean()
    avg_bytes_sent = df["bytes_sent"].mean()
    avg_bytes_recv = df["bytes_recv"].mean()


    X,y = dataframe_to_xy(df)
      

      
    old_params = get_parameters(model)
    start_time = time.time()
    train_model(model,X,y)
    training_time = time.time() - start_time
    #Creating one Malicious client for the test: unnatural behavious
    attacker_ids = random.sample(range(10),3)
    # attacker_ids = []
    attack_type = "normal"
    if partition_id in attacker_ids:
        attack_type = apply_attack(model)
        label = 1
    else: label = 0

    new_params = get_parameters(model)
    print("Labels:", np.unique(y))
    print("Label counts:")
    print(pd.Series(y).value_counts())
    loss,acc = evaluate_model(model,X,y)
    #Computing the Delta: the Change==========================================================
    delta = np.linalg.norm(new_params[0]-old_params[0])
    #Normalization of coefficient & intercenpt
    coef_norm = np.linalg.norm(model.coef_)
    intercept_norm = np.linalg.norm(model.intercept_)

    
    print(f"writing client Metrics with partiton id: {partition_id}")
    log_client_metric({
        "round":server_round,
        "partition_id": int(partition_id),
        "attack_type": attack_type,
        "train_accuracy": float(acc),
        "train_loss": float(loss),
        "update_norm": float(delta),
        "coef_norm": float(coef_norm),
        "intercept_norm": float(intercept_norm),
        "avg_cpu": float(avg_cpu),
        "avg_memory": float(avg_memory),
        "avg_connections": float(avg_connections),
        "avg_bytes_sent":float(avg_bytes_sent),
        "avg_bytes_recv": float(avg_bytes_recv),
        "training_time": float(training_time),
    })

    print(f"Saving data into attack dataset csv file")
    save_training_sample({
        "round":server_round,
        "partition_id": int(partition_id),
        "attack_type": attack_type,
        "train_accuracy": float(acc),
        "train_loss": float(loss),
        "update_norm": float(delta),
        "coef_norm": float(coef_norm),
        "intercept_norm": float(intercept_norm),
        "avg_cpu": float(avg_cpu),
        "avg_memory": float(avg_memory),
        "avg_connections": float(avg_connections),
        "training_time": training_time,
        "label": int(label)
    })

    #Adding a clipping 
    #1: It acts as first defense used in production FL systems
    coef_norm = np.linalg.norm(model.coef_)
    if coef_norm > 10:
        model.coef_ = model.coef_ *(10/coef_norm)

    updated = ArrayRecord.from_numpy_ndarrays(get_parameters(model))

    metrics = MetricRecord({
        "num-examples": len(X),
        "partition_id": int(partition_id),
        "train_loss": float(loss),
        "train_accuracy": float(acc),

        "update_norm": float(delta),
        "coef_norm": float(coef_norm),
        "intercept_norm": float(intercept_norm),

        "avg_cpu": float(avg_cpu),
        "avg_memory": float(avg_memory),
        "avg_connections": float(avg_connections),

        "training_time": float(training_time),
        "public_key": public_key,
    })

    content = RecordDict({
        "arrays": updated,
        "metrics": metrics,
    })
    return Message(content=content,reply_to=msg)

@app.evaluate()
def evaluate(msg:Message,context:Context):
    model = build_model()
    arrays = msg.content["arrays"]
    
    #getting the partition id or client_id 
    partition_id = context.node_config["partition-id"]

    parameters = arrays.to_numpy_ndarrays()
    set_parameters(model, parameters)

    df = collect_batch(partition_id=partition_id)
    X,y = dataframe_to_xy(df)
    loss,acc = evaluate_model(model,X,y)
    
    metrics = MetricRecord({
        "loss": float(loss),
        "accuracy": float(acc),
        "num-examples": len(X),
    })


    content = RecordDict({
        "metrics": metrics,
    })
    print("=============================================================CLIENT EVALUATION STARTED================================================================")
    return Message(content=content,reply_to=msg)