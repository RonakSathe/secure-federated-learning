import pandas as pd

INPUT_FILE = "datasets/attack_dataset.csv"
df = pd.read_csv(INPUT_FILE)
print(df["label"].value_counts())

print(
    df.groupby("label")[
        [
            "train_accuracy",
            "update_norm",
            "coef_norm",
            "intercept_norm",
        ]
    ].mean()
)