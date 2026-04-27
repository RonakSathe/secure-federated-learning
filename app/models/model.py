from sklearn.linear_model import LogisticRegression
import numpy as np

def get_model():
    model = LogisticRegression(max_iter=1000)

    #Dummy initialization 
    X = np.random.rand(10,5)
    y = np.random.randint(0,2,10)
    model.fit(X,y)
    return model
