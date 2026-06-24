import streamlit as st
import pandas as pd
import json
import joblib
from streamlit_autorefresh import st_autorefresh
import base64


#Video Trying as Background
video_path = "DCIM/cyber_bg.mp4"
def get_video_base_64(video_path):
    with open(video_path,"rb") as video_file:
        return base64.b64encode(video_file.read()).decode()

video_base64 = get_video_base_64(video_path)

st.set_page_config(
    page_title="FL Security Dashboard"
)

tab1,tab2 = st.tabs(
    [
        "Live Security Dashboard",
        "Research Results"
    ]
)

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

FEATURES = [
    "train_accuracy",
    "update_norm",
    "coef_norm",
    "intercept_norm",
    "avg_cpu",
    "avg_memory",
    "avg_connections",
    "training_time",
]


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

with tab1:
    st.title(" FLIDS Security Dashboard")

    #THE KPI Details
    st.subheader("System Overview")

    latest_round = df["round"].tail(10).max()
    latest_df = df[df["round"]==latest_round]

    total_clients = latest_df["partition_id"].nunique()
    current_round = int(latest_df["round"].max())
    suspicious_clients = len(latest_df[latest_df["status"]=="Suspicious"])
    malicious_clients = len(latest_df[latest_df["status"]=="Malicious"])
    attack_rate = round(
        (malicious_clients)/max(total_clients,1)*100,2
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

    X = df[FEATURES]
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
with tab2:
    st.header("Research Results")
    baseline = pd.read_csv("results/baseline.csv")
    attack = pd.read_csv("results/attack_fedavg.csv")
    secure = pd.read_csv("results/attack_securefedavg.csv")

    baseline_eval = pd.read_csv("results/baseline_eval.csv")
    attack_eval = pd.read_csv("results/attack_fedavg_eval.csv")
    secure_eval = pd.read_csv("results/attack_securefedavg_eval.csv")

    st.subheader("Training Accuracy Comparison")
    chart_df = pd.DataFrame({
        "Round": baseline["round"],
        "Baseline": baseline["train_accuracy"],
        "Attack+FedAvg": baseline["train_accuracy"],
        "Attack+SecureFedAvg": baseline["train_accuracy"],
    })

    st.line_chart(
        chart_df.set_index("Round")
    )

    st.subheader("Evaluation Accuracy Comparison")
    eval_df = pd.DataFrame({
        "Round": baseline_eval["round"],
        "Baseline": baseline_eval["accuracy"],
        "Attack+FedAvg": attack_eval["accuracy"],
        "Attack+SecureFedAvg": secure_eval["accuracy"],
    })

    st.line_chart(
        eval_df.set_index("Round")
    )


    st.subheader("Final Results")
    colu1,colu2,colu3 = st.columns(3)
    colu1.metric(
        "Baseline Accuracy",
        f"{baseline['train_accuracy'].iloc[-1]*100:.2f}%"
    )

    colu2.metric(
        "Attack+FedAvg",
        f"{attack['train_accuracy'].iloc[-1]*100:.2f}%"
    )

    colu3.metric(
        "SecureFedAvg",
        f"{secure['train_accuracy'].iloc[-1]*100:.2f}%"
    )


    baseline_acc = baseline["train_accuracy"].iloc[-1]
    attack_acc = attack["train_accuracy"].iloc[-1]
    secure_acc = secure["train_accuracy"].iloc[-1]

    improvement = (
        (secure_acc - attack_acc)
        /
        attack_acc
    ) * 100

    st.metric(
        "SecureFedAvg Improvement",
        f"{improvement:.2f}%"
    )

    blocked = pd.read_json("dashboard/blocked_clients.json")
    st.subheader("Detected Malicious Clients")
    print(blocked.keys())
    st.dataframe(
        [
            {
                "partition_id": record["partition_id"],
                "attack_type": record["attack_type"],
                "status": record["status"],
                "reason": record["reason"] 

            } for record in blocked["blocked_clients"]
        ]
    )


    #The Summary Card
    st.success(
        f"""
        Baseline Accuracy:
        {baseline['train_accuracy'].iloc[-1]*100:.2f}%

        Attack+FedAvg:
        {attack['train_accuracy'].iloc[-1]*100:.2f}%

        Attack+SecureFedAvg:
        {secure['train_accuracy'].iloc[-1]*100:.2f}%
        """
    )