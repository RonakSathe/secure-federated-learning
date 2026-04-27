import flwr as fl
import psutil
import time
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

#Buffer for live data
data_buffer = []

#Generating live data
def collect_data():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    connections = len(psutil.net_connections())
    net = psutil.net_io_counters()
    bytes_sent = net.bytes_sent
    bytes_recv = net.bytes_recv

    #simple labelling logic based on CPU usage
    score = 0
    if cpu > 70:
        score += 1
    if memory > 75:
        score += 1
    if connections > 50:
        score += 1
    if bytes_sent > 500000:
        score += 1
    if bytes_recv > 500000:
        score += 1
    label = 1 if score >= 2 else 0

    return [cpu, memory, connections, bytes_sent, bytes_recv,label]

#Model
model = LogisticRegression(max_iter=1000)
X_init = np.random.rand(10, 5)
y_init = np.random.randint(0, 2, 10)
model.fit(X_init, y_init)


#FLower CLient
class FLClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        return [model.coef_, model.intercept_]
    
    def set_parameters(self, parameters):
        model.coef_ = parameters[0]
        model.intercept_ = parameters[1]
    
    def fit(self, parameters, config):
        self.set_parameters(parameters)

        #Collecting live data 
        print("\n\nCOllecting live data.........")
        data_buffer.clear()

        for _ in range(50):
            data_buffer.append(collect_data())
            time.sleep(0.5)
        
        data = np.array(data_buffer)
        X = data[:, :-1]
        y = data[:, -1]
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        #Training the model
        model.fit(X, y)
        print("Training done on live data")
        return self.get_parameters(config), len(X), {}
    
    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        if len(data_buffer) < 10:
            return 0.0, 1, {"accuracy":0.0}
        data = np.array(data_buffer)
        X = data[:, :-1]
        y = data[:, -1]
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        accuracy = model.score(X, y)
        #Evaluating the loss
        y_pred_proba = model.predict_proba(X)
        loss = log_loss(y, y_pred_proba)
        print(f"Evaluation done on live data with accuracy: {accuracy:.4f} and Loss: {loss:.4f}")
        return loss, len(X), {"accuracy":accuracy}

#Start CLient
fl.client.start_numpy_client(server_address="10.184.104.183:8080", client=FLClient(),)