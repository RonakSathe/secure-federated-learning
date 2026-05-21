import streamlit as st
import pandas as pd
from pathlib import Path

LOG_PATH = Path("logs/metrics.csv")

st.set_page_config(page_title="Federated Learning Dashboard", layout="wide")
st.title("Secure FL Dashboard")

def load_metrics() -> pd.DataFrame:
    if LOG_PATH.exists():
        return pd.read_csv(LOG_PATH)
    return pd.DataFrame(columns=["round", "loss", "accuracy"])

@st.fragment(run_every=2)
def live_dashboard():
    df = load_metrics()

    if df.empty:
        st.info("Waiting for metrics from the server...")
        return
    df = df.sort_values("round").reset_index(drop=True)
    c1,c2,c3 = st.columns(3)
    c1.metric("Latest Round", int(df["round"].iloc[-1]) )
     