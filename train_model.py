import joblib
from collections import Counter
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, precision_recall_curve, auc, f1_score, roc_curve, roc_auc_score
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import TomekLinks
from preprocess import load_and_clean_data
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV, train_test_split
from lightgbm import LGBMClassifier
import time
import os

def main():
    os.makedirs('ai_model', exist_ok=True)

    print("🔄 Loading and cleaning data...")
    X_train, X_test, y_train, y_test, encoders, scaler = load_and_clean_data()
    feature_columns = X_train.columns.tolist()
    joblib.dump(feature_columns, 'ai_model/feature_columns.pkl')

    print("\n📊 Before Resampling:", Counter(y_train))

    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

    tomek = TomekLinks()
    X_resampled, y_resampled = tomek.fit_resample(X_resampled, y_resampled)

    print("📊 After Resampling:", Counter(y_resampled))

    print("\n🚀 Training model with randomized hyperparameter search...")
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [6, 10],
        'learning_rate': [0.01, 0.05],
        'num_leaves': [31, 50],
        'class_weight': [{0: 1, 1: 5}, {0: 1, 1: 10}]
    }

    lgbm = LGBMClassifier(boosting_type='gbdt', n_jobs=-1, subsample=0.8, colsample_bytree=0.8, random_state=42)
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    # Optional: speed up by using subset
    X_tune, _, y_tune, _ = train_test_split(X_resampled, y_resampled, train_size=0.3, stratify=y_resampled, random_state=42)

    search = RandomizedSearchCV(
        lgbm,
        param_distributions=param_grid,
        n_iter=10,
        cv=skf,
        scoring='f1',
        verbose=2,
        n_jobs=-1,
        random_state=42
    )
    best_thresh = thresholds[np.argmax(f1_scores)]
    with open('ai_model/threshold.txt', 'w') as f:
    f.write(str(best_thresh))

    start = time.time()
    search.fit(X_tune, y_tune)
    print(f"⏱️ Search completed in {(time.time() - start)/60:.2f} minutes")
    print(f"\n✅ Best Parameters: {search.best_params_}")

    model = search.best_estimator_

    print("\n🔧 Tuning decision threshold...")
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    thresholds = np.arange(0.1, 0.9, 0.01)
    f1_scores = [f1_score(y_test, (y_pred_proba > t).astype(int)) for t in thresholds]
    best_thresh = thresholds[np.argmax(f1_scores)]
    print(f"\n🏁 Best Threshold: {best_thresh:.2f} → F1 Score: {max(f1_scores):.4f}")
    y_pred = (y_pred_proba > best_thresh).astype(int)

    print("\n📈 Evaluating model...")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    report = classification_report(y_test, y_pred, output_dict=True)
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    print(f"Recall (Fraud): {report['1']['recall']:.4f}")
    print(f"Precision (Fraud): {report['1']['precision']:.4f}")
    print(f"F1-score (Fraud): {report['1']['f1-score']:.4f}")

    print("\n🧩 Confusion Matrix")
    conf_matrix = confusion_matrix(y_test, y_pred)
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Not Fraud', 'Fraud'], yticklabels=['Not Fraud', 'Fraud'])
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig('ai_model/confusion_matrix.png')
    plt.close()

    print("\n📉 Precision-Recall and ROC curves...")
    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    auc_pr = auc(recall, precision)
    plt.plot(recall, precision, label=f'AUC-PR = {auc_pr:.2f}')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend()
    plt.grid(True)
    plt.savefig('ai_model/precision_recall_curve.png')
    plt.close()

    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    plt.plot(fpr, tpr, label=f'AUC-ROC = {roc_auc:.2f}')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.grid(True)
    plt.savefig('ai_model/roc_curve.png')
    plt.close()

    print("\n📌 Feature Importance")
    importances = model.feature_importances_
    feature_df = pd.DataFrame({'Feature': X_train.columns, 'Importance': importances}).sort_values(by='Importance', ascending=False)
    sns.barplot(x='Importance', y='Feature', data=feature_df.head(15))
    plt.title('Top 15 Feature Importances')
    plt.tight_layout()
    plt.savefig('ai_model/feature_importance.png')
    plt.close()

    print("\n💾 Saving model and encoders...")
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    joblib.dump(model, f'ai_model/model_{timestamp}.pkl')
    joblib.dump(encoders, f'ai_model/encoder_{timestamp}.pkl')
    joblib.dump(scaler, f'ai_model/scaler_{timestamp}.pkl')

    print("\n✅ All assets saved to 'ai_model/'")

if __name__ == '__main__':
    main()
