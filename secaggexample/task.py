from __future__ import annotations

import random
import time
from dataclasses import dataclass
import numpy as np
import pandas as pd
import psutil
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from flwr.clientapp import ClientApp
from flwr.client.mod import secaggplus_mod
from flwr.app import Context
from flwr.client import NumPyClient

FEATURE_NAMES = ["cpu","memory","connections","bytes_sent","bytes_recv"]

@dataclass
class LiveSample:
    cpu:float
    memory:float
    connections:float
    bytes_sent:float
    bytes_recv:float
    label:int

def collect_sample() -> LiveSample:
    """Collect one real-time telemetry sample from the  machine."""
    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory().percent
    connections = float(len(psutil.net_connections()))
    net = psutil.net_io_counters()
    bytes_sent = float(net.bytes_sent)
    bytes_recv = float(net.bytes_recv)
    
    #Heuristic label for yuor intrusion-detection demo
    score = 0
    if cpu > 60:
        score += 1
    if memory > 70:
        score += 1
    if connections > 30:
        score += 1
    if bytes_sent > 200000:
        score += 1
    if bytes_recv > 200000:
        score += 1
    label = 1 if score >= 2 else 0
    return LiveSample(
        cpu=cpu,
        memory=memory,
        connections=connections,
        bytes_sent=bytes_sent,
        bytes_recv=bytes_recv,
        label=label
    )

def collect_batch(num_samples: int=50,delay_range:tuple[float,float]=(0.1,0.5)) ->pd.DataFrame:
    """Collect a batch of real-time telemetry samples."""
    rows = []
    for _ in range(num_samples):
        s = collect_sample()
        rows.append({
            "cpu": s.cpu,
            "memory": s.memory,
            "connections": s.connections,
            "bytes_sent": s.bytes_sent,
            "bytes_recv": s.bytes_recv,
            "label": s.label
        })
        time.sleep(random.uniform(*delay_range))
    return pd.DataFrame(rows)

def build_model() -> LogisticRegression:
    """Build a simple logistic regression model for intrusion detection."""
    model = LogisticRegression(max_iter = 1000)

    #Dummy fit so coef / intercept exist before FL starts
    X_init = np.random.rand(10,len(FEATURE_NAMES))
    y_init = np.random.randint(0,2,10)
    model.fit(X_init,y_init)
    return model

def ensure_two_classes(y:np.ndarray) -> np.ndarray:
    """Ensure training data has at least  2 classes"""
    if len(np.unique(y))<2:
        y = y.copy()
        y[0] = 1- y[0]
    return y

def train_model(model: LogisticRegression, X:np.ndarray, y:np.ndarray) -> LogisticRegression:
    """Train the model on lacal data."""
    y = ensure_two_classes(y)
    model.fit(X,y)
    return model

def evaluate_model(model: LogisticRegression, X: np.ndarray, y:np.ndarray)-> tuple[float,float]:
    """Return (loss, accuracy)"""
    y = y.astype(int)
    y_pred = model.predict(X)
    accuracy = accuracy_score(y,y_pred)

    if len(np.unique(y))<2:
        print("We got the same values overall so log loss is not defined. Returning 0.0")
        loss = 0.0 
    else:
        y_pred_proba = model.predict_proba(X)
        loss = log_loss(y,y_pred_proba, labels = [0,1])
    return float(loss), float(accuracy)

def dataframe_to_xy(df:pd.DataFrame)-> tuple[np.ndarray,np.ndarray]:
    """COnverting a telemetry dataframe into X & y"""
    X = df[FEATURE_NAMES].to_numpy(dtype=float)
    y = df["label"].to_numpy(dtype=int)
    return X,y

#Build one shared model instance
model = build_model()

class IDSClient(NumPyClient):
    def __init__(self,partition_id:int):
        self.partition_id = partition_id
        self.local_data = collect_batch()
    
    def get_parameters(self, config):
        return [model.coef_, model.intercept_]
    
    def set_parameter(self,parameters):
        model.coef_ = parameters[0]
        model.intercept_ = parameters[1]
    
    def fit(self,parameters,config):
        self.set_parameter(parameters)
        self.local_data = collect_batch()
        X,y = dataframe_to_xy(self.local_data)
        train_model(model,X,y)
        return [ model.coef_,model.intercept_],len(X),{}
    
    def evaluate(self, parameters, config):
        self.set_parameter(parameters)
        X,y = dataframe_to_xy(self.local_data)
        loss,accuracy = evaluate_model(model,X,y)
        return float(loss),len(X),{"accuracy": float(accuracy)}
    
def create_client(partition_id:int):
    return IDSClient(partition_id)
