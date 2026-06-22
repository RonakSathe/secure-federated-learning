import streamlit as st
import pandas as pd
import json
from functionalities import calculate_trust_score
import joblib
from streamlit_autorefresh import st_autorefresh
import base64


#Video Trying as Background
video_path = "DCIM/cyber_bg.mp4"
def get_video_base_64(video_path):
    with open(video_path,"rb") as video_file:
        return base64.b64encode(video_file.read()).decode()

video_base64 = get_video_base_64(video_path)

st.markdown(
    f"""
    <style>

    #bg-video {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        object-fit: cover;
        z-index: -1;
        opacity: 0.50;
    }}

    .stApp {{
        background: transparent;
    }}

    </style>

    <video autoplay muted loop id="bg-video">
        <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
    </video>

    """,
    unsafe_allow_html=True,
)




###########################################################
#############################################################

count = st_autorefresh(
    interval=3000,
    key="dashboard_refresh"
)
st.caption(f"Dashboard refreshed {count} times ")

#Loading Mdel
mlp_model = joblib.load("models/mlp_attack_detector.pkl")
scaler = joblib.load("models/mlp_scaler.pkl")



st.set_page_config(
    page_title="Real-TIme Intrusion Detecction & MOdel Poisoning Monitoring Dashboard",
    layout="wide"
)


with open("dashboard/client_metrics.json","r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

st.title(" FLIDS Security Dashboard")

#THE KPI Details
st.subheader("System Overview")

latest_round = df["round"].max()
latest_df = df[df["round"]==latest_round]

total_clients = latest_df["partition_id"].nunique()
current_round = int(df["round"].max())
suspicious_clients = len(latest_df[latest_df["status"]=="Suspicious"])
malicious_clients = len(latest_df[latest_df["status"]=="Malicious"])
attack_rate = round(
    malicious_clients/max(total_clients,1)*100,2
)

col1,col2,col3,col4,col5 = st.columns(5)
col1.metric("Total CLients",total_clients)
col2.metric("Current Round",current_round)
col3.metric("Suspicious Clients",suspicious_clients)
col4.metric("Malicious Clients",malicious_clients)
col5.metric("Attack Rate %", attack_rate)



st.subheader("Raw Metrics")
st.dataframe(df)

#Building Features:
FEAUTRES = [
    "update_norm",
    "coef_norm",
    "intercept_norm",
    "avg_cpu",
    "avg_memory",
    "avg_connections",
    "training_time",
]

X = df[FEAUTRES]
X_scaled = scaler.transform(X)

predictions = mlp_model.predict(X_scaled)
probabilities = mlp_model.predict_proba(X_scaled)

#Adding Results
df["predictions"] = predictions
df["attack_confidence"] = (
    probabilities[:,1] *100
)

df["status"] = df["predictions"].map(
    {
        0:"Normal",
        1:"Malicious"
    }
)


#MLP Detection
st.subheader("MLP Attack Detection")

st.dataframe(
    df[
        [
            "round",
            "partition_id",
            "attack_type",
            "update_norm",
            "status",
            "attack_confidence"
        ]
    ]
)


#High Risk CLients
st.subheader("Highest RIsk Cients")
st.dataframe(
    df.sort_values(
        "attack_confidence",
        ascending=False
    ).head(10)
)

#COnfidence Chart
st.subheader("Attack Confidence Chart")
st.bar_chart(
    df.set_index(
        "partition_id"
    )["attack_confidence"]
)
