import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os

def load_and_clean_data(data_path='Bank_Account_Fraud_Dataset_Suite.csv'):
    print("📂 Loading dataset...")
    df = pd.read_csv(data_path)

    original_len = len(df)
    df.dropna(inplace=True)
    print(f"✅ Dropped {original_len - len(df)} rows with missing values.")

    if 'fraud_bool' not in df.columns:
        raise ValueError("❌ Target column 'fraud_bool' not found in dataset!")

    y = df['fraud_bool']
    X = df.drop(columns=['fraud_bool'])

    # Convert date columns
    for col in [c for c in X.columns if 'Date' in c]:
        X[col] = pd.to_datetime(X[col], errors='coerce')
        X[f'{col}_month'] = X[col].dt.month.fillna(0).astype(int)
        X[f'{col}_year'] = X[col].dt.year.fillna(0).astype(int)
        X.drop(columns=[col], inplace=True)

    # Encode categoricals
    encoders = {}
    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].fillna("Missing").astype(str))
        encoders[col] = le

    # Scale features
    feature_names = X.columns.tolist()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X = pd.DataFrame(X_scaled, columns=feature_names)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.2, random_state=42
    )

    # Save preprocessing artifacts
    os.makedirs('ai_model', exist_ok=True)
    joblib.dump(encoders, 'ai_model/encoder.pkl')
    joblib.dump(scaler, 'ai_model/scaler.pkl')
    joblib.dump(feature_names, 'ai_model/feature_names.pkl')

    # Save cleaned dataset
    df_cleaned = X.copy()
    df_cleaned['fraud_bool'] = y.values
    df_cleaned.to_csv('ai_model/cleaned_dataset.csv', index=False)
 
    print("✅ Preprocessing complete.")
    return X_train, X_test, y_train, y_test, encoders, scaler
