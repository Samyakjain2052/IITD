import pandas as pd
import xgboost as xgb
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report

# Load the dataset
print("Loading dataset...")
df = pd.read_csv("job_titles_dataset_5000.csv")
print(f"Dataset shape: {df.shape}")

# Convert job type to binary values
df["Job Type"] = df["Job Type"].map({"Technical": 1, "Non-Technical": 0})
print(f"\nClass distribution:\n{df['Job Type'].value_counts(normalize=True)}")

# Apply TF-IDF vectorization with improved parameters
tfidf = TfidfVectorizer(
    max_features=1000,
    stop_words='english',
    ngram_range=(1, 2)
)
X = tfidf.fit_transform(df["Job Title"])
y = df["Job Type"]

# Split data with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train XGBoost model with tuned parameters
model = xgb.XGBClassifier(
    objective="binary:logistic",
    eval_metric="logloss",
    max_depth=6,
    learning_rate=0.1,
    n_estimators=200,
    colsample_bytree=0.8,
    subsample=0.8
)

print("\nTraining model...")
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Non-Technical", "Technical"]))

# Save model and vectorizer
print("\nSaving model and vectorizer...")
with open("model.pkl", "wb") as model_file:
    pickle.dump(model, model_file)
with open("tfidf.pkl", "wb") as tfidf_file:
    pickle.dump(tfidf, tfidf_file)
print("Model and vectorizer saved successfully!")

# Test predictions
test_titles = [
    "Software Engineer",
    "Marketing Manager",
    "Data Scientist",
    "HR Coordinator"
]

print("\nTesting predictions:")
for title in test_titles:
    vec = tfidf.transform([title])
    pred = model.predict(vec)[0]
    prob = model.predict_proba(vec)[0]
    job_type = "Technical" if pred == 1 else "Non-Technical"
    confidence = prob[1] if pred == 1 else prob[0]
    print(f"{title}: {job_type} (confidence: {confidence:.2%})")