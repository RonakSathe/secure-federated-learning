#Creating the dashboard 
import streamlit as st
from pathlib import Path
import json

BASE_DIR = Path(__file__).parent

metrics_file = BASE_DIR/"metrics.json"
#set the tile
st.title("Federated Learning Dashboard")

#opening file: 
with open(metrics_file,"r") as f:
    
    #data variable holding all the contents of the metrics.json file as json
    data = json.load(f)

    st.metric(
        "Current Round",
        data["round"]
    )

    st.metric(
        "Accuracy",
        data["accuracy"]
    )

    st.metric(
        "Loss",
        data["loss"]
    )

    st.metric(
        "Clients",
        data["clients"]
    )
