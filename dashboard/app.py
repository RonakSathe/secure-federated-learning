#Creating the dashboard 
import streamlit as st
from pathlib import Path
import json
import pandas as pd

st.set_page_config(
    page_title="Federated Learning Dashboard",
    layout="wide"
)

BASE_DIR = Path(__file__).parent

metrics_file = BASE_DIR/"metrics.json"
#set the tile
st.title("Federated Learning Dashboard")

#opening file: 
with open(metrics_file,"r") as f:    
    #data variable holding all the contents of the metrics.json file as json
    data = json.load(f)
train_df = pd.DataFrame.from_dict(data["train_metrics"],orient="index")
eval_df = pd.DataFrame.from_dict(data["evaluate_metrics"],orient="index")
train_df.index.name = "Round"
eval_df.index.name = "Round"

st.header("Training Summary")
col1,col2,col3,col4 = st.columns(4)

latest_train_acc = train_df["train_accuracy"].iloc[-1]
latest_train_loss = train_df["train_loss"].iloc[-1]

latest_eval_acc = eval_df["accuracy"].iloc[-1]
latest_eval_loss = eval_df["loss"].iloc[-1]

col1.metric(
    "Train Accuracy",
    f"{latest_train_acc:.4f}"
)

col2.metric(
    "Train loss",
    f"{latest_eval_loss:.4f}"
)

col3.metric(
    "Eval Accuracy",
    f"{latest_eval_acc:.4f}"
)

col4.metric(
    "Eval loss",
    f"{latest_eval_loss:.4f}"
)

#Accuracy Chart
st.header("Accuracy Over Rounds")
accuracy_df = pd.DataFrame({
    "Train Accuracy": train_df["train_accuracy"],
    "Eval Accuracy": eval_df["accuracy"]
})

st.line_chart(accuracy_df)

#Loss Chart
st.header("Loss Over Rounds")
loss_df = pd.DataFrame({
    "Train Loss": train_df["train_loss"],
    "Eval Loss": eval_df["loss"]
})

st.line_chart(loss_df)


#Raw Metrics
st.header("Training Metrics")
st.dataframe(train_df)
st.header("Evaluation Metrics")
st.dataframe(eval_df)