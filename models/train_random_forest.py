import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import ( accuracy_score,classification_report,confusion_matrix)
from sklearn.ensemble import RandomForestClassifier

#Load Dataset
df = pd.read_csv("datasets/attack_dataset_clean.csv")
print(df.head())
print(df["label"].value_counts())

#Selecting Features
FEATURES = [
    "update_norm",
    "coef_norm",
    "intercept_norm",
    "avg_cpu",
    "avg_memory",
    "avg_connections",
    "training_time",
]

#Selecting the data X & y
X = df[FEATURES]
y = df["label"]

#Train,Test, SPlit the data
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state= 42,stratify= y)

#Training the model 
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced",
)
model.fit(X_train,y_train)

#Evalutating the model
pred = model.predict(X_test)
print(
    "\n\n Accuracy:",accuracy_score(y_test,pred)
)

print(
    "Classification Report",
    classification_report(y_test,pred)
)

print(
    "Confusion mAtrix",
    confusion_matrix(y_test,pred)
)

# #Saving THe MOdel
# joblib.dump(
#     model,"models/attack_detector.pkl"
# )

#Getting importance feature
importance_metric = model.feature_importances_
for name , score in zip(FEATURES,importance_metric):
    print(f"{name}: {score:.4f}")
