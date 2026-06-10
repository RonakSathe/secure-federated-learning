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

    model = build_model()

    arrays = msg.content["arrays"]

    paramters = arrays.to_numpy_ndarrays()
    set_parameters(model, paramters)

    df = collect_batch()
    X,y = dataframe_to_xy(df)

    train_model(model,X,y)

    updated = ArrayRecord.from_numpy_ndarrays(get_parameters(model))

    metrics = MetricRecord({
        "num-examples": len(X)
    })

    content = RecordDict({
        "arrays": updated,
        "metrics": metrics,
    })
    return Message(content=content,
                   reply_to=msg,
                   )

@app.evaluate()
def evaluate(msg:Message,context:Context):
    model = build_model()
    arrays = msg.content["arrays"]

    parameters = arrays.to_numpy_ndarrays()
    set_parameters(model, parameters)

    df = collect_batch()
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

    return Message(content=content,reply_to=msg)