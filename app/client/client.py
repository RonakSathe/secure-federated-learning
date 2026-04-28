CLIENT_ID = 0
import flwr as fl
import numpy as np
import time
import random
from app.models.model import get_model
from app.client.data_collector import collect_data
from app.client.trainer import label_data
from app.client.security import encrypt_params,decrypt_params
from app.utils.config import SERVER_ADDRESS
from app.client.secure_agg import apply_mask


model = get_model()
data_buffer = []

def is_suspicious(old_params,new_params,threshold=5.0):
    old_coef,old_intercept = old_params
    new_coef,new_intercept = new_params

    diff = np.linalg.norm(new_coef - old_coef) + np.linalg.norm(new_intercept - old_intercept)
    print(f"Update magnitude: {diff:.4f}")
    return diff > threshold

class FLClient(fl.client.NumPyClient):

    def get_parameters(self,config):
        print("Getting parameters from server...")
        params = [model.coef_.copy(), model.intercept_.copy()]
        # return [encrypt_params(params)]
        return apply_mask(params, CLIENT_ID)
    
    def set_parameters(self,parameters):
        print("Received parameters from servers...")
        model.coef_,model.intercept_ = parameters
    
    def fit(self,parameters,config):
        self.set_parameters(parameters)
        old_params = [model.coef_.copy(), model.intercept_.copy()]

        print("Collecting live data...")
        data_buffer.clear()

        for _ in range(50):
            d = collect_data()
            d.append(label_data(d))
            data_buffer.append(d)
            time.sleep(random.uniform(0.1,0.5))
        
        data = np.array(data_buffer)
        X = data[:,:-1]
        y = data[:,-1]

        if len(set(y)) < 2:
            print(" Only one class detected, skipping training...")
            return self.get_parameters(config), len(X), {}

        print("Training model on collected data...")
        model.fit(X,y)

        if random.random() < 0.3:
            print("Malicious client !!! Injecting noise....")
            model.coef *= np.random.uniform(0.5,1.5,size=model.coef_.shape)
            model.intercept *= np.random.uniform(0.5,1.5,size=model.intercept_.shape)
        
        new_params = [model.coef_, model.intercept_]
        if is_suspicious(old_params,new_params):
            print("Suspicious update detected! Aborting...")
            return self.get_parameters(config), len(X), {}
        print("Update accepted. Sending parameters to server...")
        return self.get_parameters(config), len(X), {}
    
    def evaluate(self,parameters,config):
        self.set_parameters(parameters)

        if len(data_buffer) == 0:
            return 0.0, 1, {"accuracy": 0.0}
        
        data = np.array(data_buffer)
        X = data[:,:-1]
        y = data[:,-1]
        
        accuracy = model.score(X,y)
        print(f"Evaluating model... Accuracy: {accuracy:.4f}")
        return 0.0, len(X), {"accuracy": accuracy}

def start_client():
    print("Starting FL client...")
    fl.client.start_numpy_client(
        server_address=SERVER_ADDRESS,
        client=FLClient()
        )