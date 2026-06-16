from flwr.clientapp import ClientApp
from datetime import datetime
import numpy as np
from flwr.app import (
    Message,
    Context,
    RecordDict,ArrayRecord,MetricRecord,
)
from .task import *
from .logger import log_client_metric

#Trainig data

app = ClientApp()


@app.train()
def train(msg:Message,context:Context):
    model = build_model()
    arrays = msg.content["arrays"]
    config = msg.content["config"]

    print(f"\n\n ==========x=x=x=x=x============Message contnet keys: {msg.content.keys()}")

    print(f"\n\n\n  Message COntent: {msg.content}")
    server_round = msg.content["config"]["server-round"]

    #getting the partition id or client_id 
    partition_id = context.node_config["partition-id"]
    print(f"Partition ID: {partition_id}")
    
    paramters = arrays.to_numpy_ndarrays()
    set_parameters(model, paramters)

    df = collect_batch(partition_id=partition_id)
    X,y = dataframe_to_xy(df)
    
    
    old_params = get_parameters(model)
    train_model(model,X,y)
    #Creating one Malicious client for the test: unnatural behavious
    if partition_id == 2:
        print("\n\n\n xxxxxxxxxxxxxxxxxxxxxxxxx MALICIOUS ! CLIENT ! DETECTED ! xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ")
        print(f"\n Partition id: {partition_id}")
        model.coef_ *= 100

    new_params = get_parameters(model)
    loss,acc = evaluate_model(model,X,y)


    #Computing the Delta: the Change==========================================================
    delta = np.linalg.norm(new_params[0]-old_params[0])
    print(f"writing client Metrics wiht partiton id: {partition_id}, Delta: {delta}")
    log_client_metric({
        "round":server_round,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "partition_id": int(partition_id),
        "train_accuracy": float(acc),
        "train_loss": float(loss),
        "update_norm": float(delta),
    })

    #Adding a clipping 
    #1: It acts as first defense used in production FL systems
    coef_norm = np.linalg.norm(model.coef_)
    if coef_norm > 10:
        model.coef_ = model.coef_ *(10/coef_norm)


    updated = ArrayRecord.from_numpy_ndarrays(get_parameters(model))

    metrics = MetricRecord({
        "num-examples": len(X),
        "train_loss": float(loss),
        "train_accuracy": float(acc),

    })

    print(f"Model Coefficient: {model.coef_}")
    print(f"Model Intercept: {model.intercept_}")

    content = RecordDict({
        "arrays": updated,
        "metrics": metrics,
    })
    print("===========================================CLIENT TRAINING STTARTED====================================================================")
    return Message(content=content,
                   reply_to=msg,
                   )

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