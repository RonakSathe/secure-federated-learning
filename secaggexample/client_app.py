from flwr.clientapp import ClientApp
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

    print("\n\n :::::::Context Details::::::::::",context)
    model = build_model()
    arrays = msg.content["arrays"]

    #getting the partition id or client_id 
    partition_id = context.node_config["partition-id"]


    paramters = arrays.to_numpy_ndarrays()
    set_parameters(model, paramters)

    df = collect_batch(partition_id=partition_id)
    X,y = dataframe_to_xy(df)
    print("=========================Total Samples: ==============================", len(X))
    print("\n\n partition_id:;",partition_id,X[:,0].mean(),X[:,1].mean(),X[:,2].mean())
    train_model(model,X,y)

    updated = ArrayRecord.from_numpy_ndarrays(get_parameters(model))

    metrics = MetricRecord({
        "num-examples": len(X),
        "partition-id": partition_id,
    })

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