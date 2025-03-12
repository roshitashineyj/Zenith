import os
import time
import pandas as pd
import numpy as np
from sklearn.experimental import enable_iterative_imputer  # Required for IterativeImputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# File paths (Ensure these are correct)
DATASET_CSV = r"C:\Zenith\ssnmldatairrig.csv"  # Raw string for Windows paths
SENSOR_CSV = r"C:\Zenith\sensor_datas.csv"
WEATHER_CSV = r"C:\Zenith\weather_data.csv"

# Load dataset and preprocess
def load_dataset():
    print("📂 Loading dataset...")

    # Read dataset
    df = pd.read_csv(DATASET_CSV)

    # Convert 'ON'/'OFF' in 'Status' column to 1/0
    df['Status'] = df['Status'].replace({'ON': 1, 'OFF': 0}).infer_objects(copy=False)

    # Ensure all values are numeric
    df['Status'] = df['Status'].astype(int)

    # Handle missing values using IterativeImputer
    imputer = IterativeImputer()
    df.iloc[:, :] = imputer.fit_transform(df)

    # Separate features (X) and target (y)
    X = df.drop(columns=['Status'])
    y = df['Status']

    # Apply MinMaxScaler
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    print("✅ Dataset loaded and preprocessed.")
    return X_scaled, y, scaler, X.columns  # Return column names for consistency

# Fetch latest sensor and weather data
def get_latest_data(expected_columns):
    print("🔄 Fetching latest sensor & weather data...")

    try:
        sensor_df = pd.read_csv(SENSOR_CSV)
        weather_df = pd.read_csv(WEATHER_CSV, encoding='ISO-8859-1')  # Handles encoding issues

        # Extract last row from sensor CSV
        sensor_values = sensor_df.iloc[-1, :4].values.tolist()  # Extract the first 4 columns

        # Extract last row from weather CSV
        weather_df = weather_df.iloc[:, 1:].astype(float) #convert to numeric.
        weather_values = weather_df.iloc[-1, -5:].values.tolist() #get last 5 cols, and convert to list.

        # Combine sensor & weather data
        input_values = sensor_values + weather_values

        # Ensure feature consistency
        if len(input_values) != len(expected_columns):
            raise ValueError(f"Expected {len(expected_columns)} features, but got {len(input_values)}.")

        print(f"✅ Latest Input Data: {input_values}")
        return np.array(input_values)

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

# Train and evaluate KNN model
def train_knn(X, y):
    print("🚀 Training KNN Model...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train, y_train)

    y_pred = knn.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred) * 100

    print(f"✅ KNN Model Accuracy: {accuracy:.2f}%")
    return knn

# Main function
def main():
    # Load dataset
    X, y, scaler, expected_columns = load_dataset()

    # Train KNN model
    knn = train_knn(X, y)

    while True:
        # Get latest sensor & weather data
        input_values = get_latest_data(expected_columns)
        if input_values is not None:
            input_values_scaled = scaler.transform([input_values.reshape(1, -1)])  # Scale input values, reshape for scaler
            prediction = knn.predict(input_values_scaled)[0]
            status = "ON" if prediction == 1 else "OFF"

            print(f"⚡ Predicted Irrigation Status: {status}")

        # Wait 30 minutes before next check
        print("⏳ Waiting for next cycle...\n")
        time.sleep(1)  # 1800 seconds = 30 minutes

if __name__ == "__main__":
    main()