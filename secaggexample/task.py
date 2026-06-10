from __future__ import annotations
import random
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
import psutil
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,log_loss

FEATURE_NAMES = ["cpu", "memory", "connections","bytes_sent", "bytes_recv"]

@dataclass
class LiveSample:
    cpu:float
    memory:float
    connections:float
    bytes_sent:float
    bytes_recv:float
    label:int

def collect_sample() -> LiveSample:
    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory().percent
    connections = float(len(psutil.net_connections()))
    net = psutil.net_io_counters()
    bytes_sent = float(net.bytes_sent)
    bytes_recv = float(net.bytes_recv)

    score=0
    if cpu > 50: score+=1
    if memory > 50: score+=1
    if connections > 30: score+=1
    if bytes_sent > 200000: score+=1
    if bytes_recv > 200000: score+=1
    label = 1 if score >= 3 else 0
    return LiveSample(cpu=cpu, memory=memory, connections=connections, bytes_sent=bytes_sent, bytes_recv=bytes_recv, label=label)

def collect_batch(partition_id:int,samples_size:int=50,delay_range:tuple[float,float]=(0.1,0.3)) -> pd.DataFrame:
    records = []
    for _ in range(samples_size):
        record = collect_sample()
        record.cpu += 10 if partition_id == 0 else (20 if partition_id == 1 else 15) 
        record.connections += 100000 if partition_id == 0 else (200000 if partition_id == 1 else 150000)
        records.append({
            "cpu": record.cpu,
            "memory": record.memory,
            "connections": record.connections,
            "bytes_sent": record.bytes_sent,
            "bytes_recv": record.bytes_recv,
            "label": record.label
        })
        time.sleep(random.uniform(*delay_range))
    return pd.DataFrame(records)

def build_model() -> LogisticRegression:
    model = LogisticRegression()
    #Dumy fit so coef_ & intercept_ exist in true nature
    X_init = np.random.rand(10,len(FEATURE_NAMES))
    y_init = np.random.randint(0,2,size=10)
    model.fit(X_init,y_init)
    return model

def ensure_two_classes(y:np.ndarray)->np.ndarray:
    if len(np.unique(y)) < 2:
        y = y.copy()
        y[0] = 1 - y[0]
    return y

def dataframe_to_xy(df: pd.DataFrame) -> tuple[np.ndarray,np.ndarray]:
    X = df[FEATURE_NAMES].to_numpy(dtype=float)
    y = df["label"].to_numpy(dtype=int)
    return X, y

def train_model(model:LogisticRegression, X:np.ndarray,y: np.ndarray) -> None:
    y = ensure_two_classes(y)
    model.fit(X,y)

def evaluate_model(model:LogisticRegression, X:np.ndarray,y: np.ndarray) -> tuple[float,float]:
    y = y.astype(int)
    y_pred = model.predict(X)
    accuracy = accuracy_score(y,y_pred)
    if len(np.unique(y)) < 2:
        loss = 0.0
    else:
        y_pred_proba = model.predict_proba(X)
        loss = log_loss(y,y_pred_proba, labels = [0,1])
    return float(loss),float(accuracy)

def set_parameters(model:LogisticRegression,parameters:list[np.ndarray]) -> None:
    model.coef_ = parameters[0]
    model.intercept_ = parameters[1]

def get_parameters(model:LogisticRegression) -> list[np.ndarray]:
    return [model.coef_, model.intercept_]