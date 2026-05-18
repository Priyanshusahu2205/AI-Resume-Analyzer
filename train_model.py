import os
import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
import joblib
from dotenv import load_dotenv
load_dotenv()
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
from urllib.parse import quote_plus

engine = create_engine(
    f"mysql+pymysql://{username}:{quote_plus(password)}@localhost/resume_analyzer"
)
query = "SELECT * FROM training_data"

data = pd.read_sql(query, engine)

X = data["skills"]
y = data["job_role"]

model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", LogisticRegression())
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
model.fit(X_train, y_train)

preds = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, preds))
print(classification_report(y_test, preds))

params = {
    "tfidf__max_features": [500, 1000, 2000],
    "classifier__C": [0.1, 1, 10]
}
grid = GridSearchCV(model, params, cv=3, scoring="accuracy")
grid.fit(X_train, y_train)
print("Best params:", grid.best_params_)
model = grid.best_estimator_

joblib.dump(model, "model/resume_model.pkl")
print("Best CV Accuracy:", round(grid.best_score_ * 100, 2), "%")

print("Model trained successfully")