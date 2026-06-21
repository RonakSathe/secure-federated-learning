import pandas as pd

INPUT_FILE = "datasets/attack_dataset.csv"
OUTPUT_FILE = "datasets/attack_dataset_clean.csv"

#LOad CSV
df = pd.read_csv(
    INPUT_FILE,on_bad_lines="skip"
)

print("Original Shape", df.shape)

#--------------------------------
#Remove completely empty rows
#--------------------------------

df =df.dropna(how="all")

df = df[df["label"].isin([0,1])]

numeric_cols = [
    "round",
    "partition_id",
    "train_accuracy",
    "train_loss",
    "update_norm",
    "coef_norm",
    "intercept_norm",
    "avg_cpu",
    "avg_memory",
    "avg_connections",
    "training_time",
    "label",
]

for col in numeric_cols:
    df[col] = pd.to_numeric(
        df[col],errors="coerce"
    )

df = df.dropna()

df = df.drop_duplicates()

print("CLean SHape:", df.shape)

df.to_csv(OUTPUT_FILE,index=False)

print(f"Saved: {OUTPUT_FILE}")
print("\n Label DIstribution:")
print(df["label"].value_counts())

print("\n Attack_types")
if "attack_type" in df.columns:
    print(df["attack_type"].value_counts())