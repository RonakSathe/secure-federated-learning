from __future__ import annotations
import warnings
from flwr.app import ArrayRecord,Context,Message,MetricRecord,RecordDict
from flwr.client import ClientApp

from .task import *

app = ClientApp()

@app.train()
def train(msg: Message, context: Context):

    # Create fresh local model
    model = build_model()

    # Get parameters sent from server
    parameters = msg.content["arrays"].to_numpy_ndarrays()

    # Load parameters into model
    set_parameters(model, parameters)

    # Collect local telemetry
    df = collect_batch()

    X, y = dataframe_to_xy(df)

    # Train locally
    train_model(model, X, y)

    # Return updated parameters
    content = RecordDict(
        {
            "arrays": ArrayRecord(
                get_parameters(model)
            ),
            "metrics": MetricRecord(
                {
                    "num-examples": len(X),
                }
            ),
        }
    )

    return Message(
        content=content,
        reply_to=msg,
    )


@app.evaluate()
def evaluate(msg: Message, context: Context):

    model = build_model()

    parameters = msg.content["arrays"].to_numpy_ndarrays()

    set_parameters(model, parameters)

    df = collect_batch()

    X, y = dataframe_to_xy(df)

    loss, accuracy = evaluate_model(model, X, y)

    content = RecordDict(
        {
            "metrics": MetricRecord(
                {
                    "loss": float(loss),
                    "accuracy": float(accuracy),
                    "num-examples": len(X),
                }
            )
        }
    )

    return Message(
        content=content,
        reply_to=msg,
    )