import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score,classification_report,confusion_matrix
import joblib

df = pd.read_csv("datasets/attack_dataset_clean.csv")
print(df["label"].value_counts())

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

X = df[FEATURES]

y = df["label"]

X_train, X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,stratify=y,random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.fit_transform(X_test)

#Building Neural Network
model = MLPClassifier(
    hidden_layer_sizes=(32,16),
    activation="relu",
    solver="adam",
    max_iter=5000,
    random_state=42,
)

#Training the model
model.fit(X_test_scaled,y_test)

pred = model.predict(X_test_scaled)

#Evaluation
print(
    "\nAccuracy:",
    accuracy_score(y_test,pred)
)

print(
    "\nClassification Report"
)

print(
    classification_report(
        y_test,
        pred
    )
)

print(
    "\nConfusion Matrix"
)

print(
    confusion_matrix(
        y_test,
        pred
    )
)

joblib.dump(
    model,
    "models/mlp_attack_detector.pkl"
)
joblib.dump(
    scaler,
    "models/mlp_scaler.pkl"
)