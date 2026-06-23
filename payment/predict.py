# predict.py
import os
import joblib
import numpy as np
import pandas as pd

# Define expected feature columns for the model
FEATURE_COLUMNS = [
    'step', 'amount', 'oldbalanceOrg', 'newbalanceOrig',
    'oldbalanceDest', 'newbalanceDest', 'isFlaggedFraud',
    'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER'
]


# Set model path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '..', 'fraud_model', 'fraud_model.joblib')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(
    os.path.join(BASE_DIR, '..', 'fraud_model', 'fraud_model.joblib')
)

# 👇 DEBUG HERE (ADD THIS)
print("MODEL PATH:", MODEL_PATH)
print("FILE EXISTS:", os.path.exists(MODEL_PATH))
# Load model
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load model: {e}")

def predict_transaction(input_data):
    """
    input_data: dictionary of input values
    returns: prediction result dictionary
    """
    # Check for missing fields
    missing = [col for col in FEATURE_COLUMNS if col not in input_data]
    if missing:
        return {'error': f"Missing fields: {', '.join(missing)}"}

    try:
        # Convert to DataFrame with correct column order
        df = pd.DataFrame([input_data])[FEATURE_COLUMNS]

        # Predict
        proba = model.predict_proba(df)[0][1]
        prediction = 'Fraudulent' if proba > 0.5 else 'Legitimate'

        return {
            'prediction': prediction,
            'fraud_probability': round(proba, 4)
        }

    except Exception as e:
        return {'error': f"Prediction failed: {e}"}

# For testing via command line
if __name__ == "__main__":
    input_data = {
        'step': 1,
        'amount': 10000.0,
        'oldbalanceOrg': 5000.0,
        'newbalanceOrig': 0.0,
        'oldbalanceDest': 1000.0,
        'newbalanceDest': 11000.0,
        'isFlaggedFraud': 0,
        'CASH_OUT': 1,
        'DEBIT': 0,
        'PAYMENT': 0,
        'TRANSFER': 0
    }

    result = predict_transaction(input_data)
    print("Prediction Result:", result)
