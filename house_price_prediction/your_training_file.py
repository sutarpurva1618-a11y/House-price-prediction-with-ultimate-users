import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

# Load dataset
df = pd.read_csv("data.csv")

# Rename columns to match our model
df = df.rename(columns={
    "locality": "location",
    "beds": "bedrooms"
})

# Convert area to numeric (sqft)
df["area"] = df["area"].astype(str)
df["area"] = df["area"].str.replace("sqft", "")
df["area"] = df["area"].str.replace(",", "")
df["area"] = pd.to_numeric(df["area"], errors="coerce")

# 🔥 IMPORTANT FIX: Create realistic price
df["price"] = df["rent"] * 250

# Select required columns
df = df[["location", "area", "bedrooms", "bathrooms", "balconies", "rent", "price"]]

# Drop missing values
df = df.dropna()

# Features and targets
X = df[["location", "area", "bedrooms", "bathrooms", "balconies"]]
y_rent = df["rent"]
y_price = df["price"]

# One-hot encoding for location
X_encoded = pd.get_dummies(X, columns=["location"])

columns = X_encoded.columns

# Train rent model
X_train_rent, X_test_rent, y_train_rent, y_test_rent = train_test_split(
    X_encoded, y_rent, test_size=0.2, random_state=42
)

rent_model = LinearRegression()
rent_model.fit(X_train_rent, y_train_rent)

# Train price model
X_train_price, X_test_price, y_train_price, y_test_price = train_test_split(
    X_encoded, y_price, test_size=0.2, random_state=42
)

price_model = LinearRegression()
price_model.fit(X_train_price, y_train_price)

# Save models
with open("rent_model.pkl", "wb") as f:
    pickle.dump(rent_model, f)

with open("price_model.pkl", "wb") as f:
    pickle.dump(price_model, f)

with open("columns.pkl", "wb") as f:
    pickle.dump(columns, f)

print("✅ Training complete! Files saved.")