import json
from pathlib import Path

from filelock import FileLock

from .security import calculate_risk


BASE_DIR = Path(__file__).parent.parent
DASHBOARD_DIR = BASE_DIR / "dashboard"

DASHBOARD_DIR.mkdir(exist_ok=True)


def log_client_metric(metric: dict):

    path = DASHBOARD_DIR / "client_metrics.json"

    lock = FileLock(str(path) + ".lock")

    # Calculate risk
    risk, reasons = calculate_risk(metric)

    metric["risk"] = risk

    metric["reason"] = (
        ", ".join(reasons)
        if reasons
        else "Normal Activity"
    )

    metric["status"] = (
        "Malicious"
        if risk > 60
        else (
            "Suspicious"
            if 50 <= risk <= 60
            else "Normal"
        )
    )
    

    print(f"Writing metric for Client {metric.get('partition_id')}")

    with lock:

        data = []

        # Read existing file
        if path.exists():

            try:

                with open(path, "r", encoding="utf-8") as f:

                    content = f.read().strip()

                    if content:
                        data = json.loads(content)

            except (
                json.JSONDecodeError,
                FileNotFoundError,
            ):

                print(
                    "Warning: Corrupted JSON detected. Starting fresh."
                )

                data = []

        # Append new metric
        data.append(metric)

        # Rewrite entire file
        with open(path, "w+", encoding="utf-8") as f:

            json.dump(
                data,
                f,
                indent=4,
            )

    print(
        f"Successfully logged Client "
        f"{metric.get('partition_id')}"
    )