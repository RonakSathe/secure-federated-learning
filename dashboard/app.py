import streamlit as st
import pandas as pd
import json

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