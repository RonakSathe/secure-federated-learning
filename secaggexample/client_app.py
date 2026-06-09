import flwr as fl
from flwr.client import ClientApp,NumPyClient
from flwr.client.mod import secaggplus_mod
from . import task

class SecurtiyClient(NumPyClient):
    def __init__(self):
        #innitialize our local scikit-learn model shell
        self.model = task.build_model()
    
    def fit(self,parameters,config):
        #update local model with global parameters form the server
        task.set_parameters(self.model,parameters)

        #collect the fresh live batch of th  system metrics
        print("[CLIENT]  COllecting real-time system metrics for training........")
        df_train = task.collect_batch(sample_size=50)
        X,y = task.dataframe_to_xy(df_train)

        #Train the model
        task.train_model(self.model, X, y)

        #Extract the updated weights to send back
        updated_params = task.get_parameters(self.model)
        return updated_params, len(X), {}
    
    def evaluate(self,parameters,config):
        #Update paramters to evaluate the largest global model
        task.set_parameters(self.model,parameters)
                            
        #Collect evaluation metrics
        df_test = task.collect_batch(samples_size=20)
        X,y = task.dataframe_to_xy(df_test)

        loss,accuracy = task.evaluate_model(self.model, X, y)
        print(f"[CLIENT] Evaluation results - Loss: {loss}, Accuracy: {accuracy}")

        return float(loss), len(X), {"accuracy": float(accuracy)}
    
def client_fn(context):
    print("[CLIENT] Starting client with context:", context)
    return SecurtiyClient().to_client()
    
#Create the ClientApp
app = ClientApp(
    client_fn=client_fn,
    mods=[secaggplus_mod]
    )
