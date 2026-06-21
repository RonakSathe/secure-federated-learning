import json
from pathlib import Path
from .security import calculate_risk
BASE_DIR = Path(__file__).parent.parent
DASHBOARD_DIR = BASE_DIR / "dashboard"

def log_client_metric(metric: dict):

    path = DASHBOARD_DIR / "client_metrics.json"
    risk,reasons = calculate_risk(metric)

    print(f"Writing to: {path}")

    data = []

    if path.exists():
        try:
            with open(path, "r") as f:
                content = f.read().strip()

                if content:
                    data = json.loads(content)

        except (json.JSONDecodeError, FileNotFoundError):
            data = []
    
    metric["risk"] = risk
    metric["reason"] = ", ".join(reasons)

    metric["status"] = (
        "Malicious" if risk > 60 else ("Suspicious" if 50 <= risk <= 60 else "Normal")
    )

    data.append(metric)
    print(metric)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)