import streamlit as st
import pandas as pd
from pathlib import Path

LOG_PATH = Path("logs/metrics.csv")

st.set_page_config(page_title="FL Dashboard", layout="wide")
st.title("Secured Federated Learning Dashboard")

def load_metrics() -> pd.DataFrame:
    if LOG_PATH.exists():
        return pd.read_csv(LOG_PATH)
    else:
        return pd.DataFrame(columns=["round",
                                      "loss",
                                        "accuracy",
                                        "update_magnitude",
                                        "attack_flag",
                                        "client_trust",
                                        "status",
                                        ])

@st.fragment(run_every=2)
def live_dashboard():
    df = load_metrics()
    if df.empty:
        st.info("Waiting for metrics from the server...")
        return
    
    df = df.sort_values("round").reset_index(drop=True)

    c1,c2,c3 = st.columns(3)
    c1.metric("Latest Round", int(df["round"].iloc[-1]))
    c2.metric("Latest Loss", f"{df['loss'].iloc[-1]:.4f}")
    c3.metric("Latest Accuracy", f"{df['accuracy'].iloc[-1]:.2%}")

    left,right = st.columns(2)
    with left:
        st.subheader("accuracy")
        st.line_chart(df.set_index("round")[["accuracy"]])

        st.subheader("Client Trust by Round")
        st.line_chart(df.set_index("round")[["client_trust"]])
    
    with right:
        st.subheader("Loss by Round")
        st.line_chart(df.set_index("round")[["loss"]])

        st.subheader("Update Magnitude by Round")
        st.line_chart(df.set_index("round")[["update_magnitude"]])

    latest = df.iloc[-1]
    if latest["client_trust"] < 0.25:
        st.error("Low trust client detected - update blocked")
    elif latest["attack_flag"] == 1:
        st.warning("Potential attack detected - update flagged for review")
    else: st.success("Client update looks good")

    st.subheader("Attack Flag by Round")
    st.line_chart(df.set_index("round")[["attack_flag"]])

    st.subheader("Client Trust")
    st.bar_chart(df.set_index("round")[["client_trust"]])

    st.subheader("Recent Metrics Table")
    st.dataframe(df.tail(10),use_container_width=True)




live_dashboard()