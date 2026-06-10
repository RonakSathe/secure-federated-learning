from flwr.clientapp import ClientApp
import numpy as np
from flwr.app import (
    Message,
    Context,
    RecordDict,ArrayRecord,MetricRecord,
)
from .task import *

#Trainig data

app = ClientApp()


@app.train()
def train(msg:Message,context:Context):
    model = build_model()
    arrays = msg.content["arrays"]

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
        model.coef_ *= 100

    new_params = get_parameters(model)
    loss,acc = evaluate_model(model,X,y)


    #Computing the Delta: the Change==========================================================
    delta = np.linalg.norm(new_params[0]-old_params[0])
    print(f"\n\n Partition: {partition_id}")
    print(f"\n Weight Change:  the delta is: {delta}")


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