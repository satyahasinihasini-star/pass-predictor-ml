"""
model_train.py
Trains a simple ML model to predict whether a student will PASS or FAIL
based on study_hours, attendance_percent, and previous_marks.

Run this once: python model_train.py
It creates model.pkl which app.py loads to make predictions.
"""

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import pickle

# ----- Generate a synthetic but realistic dataset -----
np.random.seed(42)
n = 400

study_hours = np.random.uniform(0, 10, n)          # hours per day
attendance = np.random.uniform(40, 100, n)         # percent
previous_marks = np.random.uniform(30, 100, n)     # percent

# A simple weighted rule + noise decides pass/fail (this simulates "real" data)
score = (study_hours * 6) + (attendance * 0.5) + (previous_marks * 0.5)
score += np.random.normal(0, 8, n)  # noise
passed = (score > 75).astype(int)

df = pd.DataFrame({
    "study_hours": study_hours,
    "attendance": attendance,
    "previous_marks": previous_marks,
    "passed": passed
})

X = df[["study_hours", "attendance", "previous_marks"]]
y = df["passed"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(max_depth=4, random_state=42)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"Model trained. Test accuracy: {accuracy:.2%}")

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Saved model.pkl")
