import pandas as pd
import xgboost as xgb
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from fastapi import FastAPI
import uvicorn

# Load the dataset
df = pd.read_csv("job_titles_dataset_5000.csv")

# Convert job type to binary values
df["Job Type"] = df["Job Type"].map({"Technical": 1, "Non-Technical": 0})

# Apply TF-IDF vectorization on job titles
tfidf = TfidfVectorizer()
X = tfidf.fit_transform(df["Job Title"])
y = df["Job Type"]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define and train the XGBoost model
model = xgb.XGBClassifier(objective="binary:logistic", eval_metric="logloss")
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.4f}")

# Save the model and vectorizer
with open("model.pkl", "wb") as model_file:
    pickle.dump(model, model_file)
with open("tfidf.pkl", "wb") as tfidf_file:
    pickle.dump(tfidf, tfidf_file)

# Create FastAPI app
app = FastAPI()

# Load model and vectorizer
def load_model():
    with open("model.pkl", "rb") as model_file:
        model = pickle.load(model_file)
    with open("tfidf.pkl", "rb") as tfidf_file:
        tfidf = pickle.load(tfidf_file)
    return model, tfidf

model, tfidf = load_model()

@app.post("/predict")
def predict(job_title: str):
    job_vectorized = tfidf.transform([job_title])
    prediction = model.predict(job_vectorized)[0]
    job_type = "Technical" if prediction == 1 else "Non-Technical"
    return {"job_title": job_title, "predicted_job_type": job_type}

# Run the API
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)