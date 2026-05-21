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
from sklearn.metrics import log_loss

model = get_model()
data_buffer = []
client_trust = 1.0
trust_history = []

def is_suspicious(old_params,new_params,threshold=5.0):
    old_coef,old_intercept = old_params
    new_coef,new_intercept = new_params

    diff = np.linalg.norm(new_coef - old_coef) + np.linalg.norm(new_intercept - old_intercept)
    print(f"Update magnitude: {diff:.4f}")
    return diff > threshold

def update_trust(is_attack: int, magnitude: float)->float:
    global client_trust

    if is_attack == 1:
        client_trust -= 0.25
    elif magnitude >1.0:
        client_trust -= 0.10
    else:
        client_trust += 0.05
    client_trust = max(0.0, min(1.0, client_trust))
    trust_history.append(client_trust)
    return client_trust
class FLClient(fl.client.NumPyClient):

    def get_parameters(self,config):
        print("Getting parameters from server...")
        params = [model.coef_.copy(), model.intercept_.copy()]
        masked_coef,masked_intercept = apply_mask(params, CLIENT_ID)
        return [masked_coef, masked_intercept]
    
    def set_parameters(self,parameters):
        if len(parameters) != 2:
            print(f"Unexpected pamaeter count: {len(parameters)}")
            return

        coef, intercept = parameters
        coef = np.asarray(coef).reshape(model.coef_.shape)
        intercept = np.asarray(intercept).reshape(model.intercept_.shape)
        
        print(f"coef shape: {coef.shape}, intercept shape: {intercept.shape}")
        
        if coef.shape != model.coef_.shape or intercept.shape != model.intercept_.shape:
            print("Shape mismatch in received parameters, skipping evaluation")
            return
        
        print("Received parameters from servers...")
        model.coef_ = coef
        model.intercept_ = intercept
        
    
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
            print(" Only one class detected, fixing labels...")
            y[0] = 1 - y[0]
            
        print("Training model on collected data...")
        model.fit(X,y)

        ##
        attack_flag = 0
        client_trust = 1.0

        #Poisioning attack simulation
        if random.random() < 0.3:
            print("Malicious client !!! Injecting noise....")
            model.coef_ *= np.random.uniform(0.5,1.5,size=model.coef_.shape)
            model.intercept_ *= np.random.uniform(0.5,1.5,size=model.intercept_.shape) 
            attack_flag = 1
            client_trust = 0.3
        new_params = [model.coef_, model.intercept_]
        update_magnitude = (np.linalg.norm(new_params[0]-old_params[0])+np.linalg.norm(new_params[1]-old_params[1]))
        client_trust_value = update_trust(attack_flag, update_magnitude)

        if client_trust_value < 0.25:
            print("Client Blocked due to low trust score")
            safe_params = old_params
            masked_coef,masked_intercept = apply_mask(safe_params, CLIENT_ID)
            return [masked_coef, masked_intercept], len(X), {
                "attack_flag": attack_flag,
                "update_magnitude": float(update_magnitude),
                "client_trust": float(client_trust_value),
                "status": "blocked"
            }
        

        if is_suspicious(old_params,new_params):
            print("Suspicious update detected! Aborting...")
            attack_flag = 1
            client_trust = 0.1
            safe_params = old_params
            masked_coef,masked_intercept = apply_mask(safe_params, CLIENT_ID)
            return [masked_coef, masked_intercept], len(X), {
                "attack_flag": attack_flag,
                "update_magnitude": float(update_magnitude),
                "client_trust": float(client_trust_value),
            }
        
        print("Update accepted. Sending parameters to server...")
        params = [model.coef_.copy(), model.intercept_.copy()]
        masked_coef, masked_intercept = apply_mask(params, CLIENT_ID)
        return [masked_coef, masked_intercept], len(X), {
            "attack_flag": attack_flag,
            "update_magnitude": float(update_magnitude),
            "client_trust": float(client_trust_value),
        }
    
    def evaluate(self,parameters,config):
        try:
            self.set_parameters(parameters)
        except Exception as e:
            print("parameter load error:", e)
            return 0.0, 1, {"accuracy": 0.0}

        if len(data_buffer) == 0:
            return 0.0, 1, {"accuracy": 0.0}
        
        data = np.array(data_buffer)
        X = data[:,:-1]
        y = data[:, -1]
        
        # 🔥 Shape safety check
        if X.shape[1] != model.coef_.shape[1]:
            print("⚠️ Shape mismatch, skipping evaluation")
            return 0.0, len(X), {"accuracy": 0.0}

        try:
            y_pred_proba = model.predict_proba(X)
            loss = log_loss(y, y_pred_proba)
            accuracy = model.score(X, y)
            print(f"📊 Accuracy: {accuracy:.4f}")
            return float(loss), len(X), {"accuracy": float(accuracy)}

        except Exception as e:
            print("⚠️ Evaluation error:", e)
            return 0.0, len(X), {"accuracy": 0.0}
        
def start_client():
    print("Starting FL client...")
    fl.client.start_numpy_client(
        server_address=SERVER_ADDRESS,
        client=FLClient()
        )