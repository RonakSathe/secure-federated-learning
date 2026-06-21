import streamlit as st
import pandas as pd
import json
from functionalities import calculate_trust_score

st.set_page_config(
    page_title="FL Securtiy Dashboard",
    layout="wide"
)

st.title("Federated Learning Security Dashboard")

with open("dashboard/client_metrics.json","r") as f:
    data = json.load(f)

df = pd.DataFrame(data)
st.subheader("Raw Metrics")
st.dataframe(df)

#OVerview 
st.subheader("Overview")
col1,col2,col3,col4 = st.columns(4)
col1.metric("Total Records",len(df))
col2.metric("Total CLients",df["partition_id"].nunique())
col3.metric("Current Round",df["round"].max())
col4.metric("Max Update norn",round(df["update_norm"].max(),2))

#Round Filter
st.subheader("Round Filter")
selected_round = st.selectbox(
    "Choose Round",
    sorted(df["round"].unique())
)
round_df = df[df["round"]==selected_round]


#detecct anomalies automatically
threshold = 5
df["status"] = df["update_norm"].apply(
    lambda x: "Suspicious" if x >threshold else "Normal"
)

#CLIENT STATUS
st.subheader("Client Status")
st.dataframe(
    df[
        [
            "partition_id",
            "update_norm",
            "status"
        ]
    ]
)

#Updated Norm Graph
st.subheader("Update Norm Distribution")
st.bar_chart(df.set_index("partition_id")["update_norm"])

#Malicious CLient Summary
suspicious = df[df["update_norm"]>threshold]

st.subheader("Detected Attackers")

if len(suspicious) > 0:
    st.error(
        f"{len(suspicious)} suspicious client(s) detected"
    )
    st.dataframe(suspicious)
else:
    st.success(
        "No Suspicious clients detected"
    )

#Client History
st.subheader("Client History")
selected_client = st.selectbox(
    "Select CLient",
    sorted(df["partition_id"].unique())
)

client_df = df[df["partition_id"]==selected_client]
st.dataframe(client_df)
st.line_chart(client_df.set_index("round")["update_norm"])

#Creating Trust Column
df["trust_score"] = df["update_norm"].apply(calculate_trust_score)


#displaying trust table
st.subheader("Client Trust Scores")
trust_df = (
    df.groupby("partition_id")
    ["trust_score"].mean().reset_index()
)
st.dataframe(trust_df)


st.subheader("Trust Alerts")
low_trust = trust_df[trust_df["trust_score"]<60]
if len(low_trust) > 0:
    st.error(
        f"{len(low_trust)} Low-Trust client(s) detected"
    )
    st.dataframe(low_trust)
else:
    st.success(
        "ALl Clients trusted"
    )

#Trust Score Chart
st.subheader("Trust Score DIstribution")
st.bar_chart(
    trust_df.set_index(
        "partition_id")["trust_score"]
)
