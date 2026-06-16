import json
from pathlib import Path
BASE_DIR = Path(__file__).parent.parent
DASHBOARD_DIR = BASE_DIR / "dashboard"

def log_client_metric(metric: dict):

    path = DASHBOARD_DIR / "client_metrics.json"

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

    data.append(metric)
    print(metric)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)