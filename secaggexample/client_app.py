from __future__ import annotations
import warnings
from flwr.client import ClientApp,NumPyClient
from flwr.common import Context
app = ClientApp()
from .task import *


class IDSClient(NumPyClient):

    def __init__(self):
        self.model = build_model()

    def get_parameters(self, config):
        return get_parameters(self.model)

    def fit(self, parameters, config):

        set_parameters(self.model, parameters)

        df = collect_batch()

        X, y = dataframe_to_xy(df)

        train_model(self.model, X, y)

        return (
            get_parameters(self.model),
            len(X),
            {},
        )

    def evaluate(self, parameters, config):

        set_parameters(self.model, parameters)

        df = collect_batch()

        X, y = dataframe_to_xy(df)

        loss, accuracy = evaluate_model(
            self.model,
            X,
            y,
        )

        return (
            float(loss),
            len(X),
            {"accuracy": float(accuracy)},
        )


def client_fn(context: Context):
    return IDSClient().to_client()


app = ClientApp(client_fn=client_fn)