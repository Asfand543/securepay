# Fraud Detection with Machine Learning

This project demonstrates the application of machine learning models for detecting fraudulent transactions in a dataset. The analysis includes data preprocessing, visualization, and model training with evaluation metrics.

## Features
- **Data Analysis**: Performed exploratory data analysis (EDA) using `pandas`, `seaborn`, and `matplotlib` to understand the dataset's structure and key patterns.
- **Data Preprocessing**: Encoded categorical variables and removed irrelevant columns to prepare the data for model training.
- **Machine Learning Models**: Utilized multiple machine learning models, including Logistic Regression, XGBoost, and Random Forest, to predict fraudulent transactions.
- **Performance Evaluation**: Assessed models using ROC-AUC scores and confusion matrices for both training and testing datasets.

## Libraries Used
- `numpy`
- `pandas`
- `matplotlib`
- `seaborn`
- `xgboost`
- `sklearn`

## Steps in the Project

### 1. Data Loading
- Loaded the dataset using `pandas.read_csv` and explored it using `.head()`, `.info()`, and `.describe()`.
- Identified categorical, integer, and float variables in the dataset.

### 2. Data Visualization
- Visualized categorical data distribution using `sns.countplot`.
- Analyzed relationships between features using `sns.barplot`.
- Generated a correlation heatmap to identify relationships among numerical features.

### 3. Feature Engineering
- Used one-hot encoding to handle categorical variables (`type`).
- Dropped irrelevant columns (`type`, `nameOrig`, `nameDest`).

### 4. Model Training
- Split the data into training and testing sets using `train_test_split`.
- Trained the following machine learning models:
  - Logistic Regression
  - XGBoost Classifier
  - Random Forest Classifier

### 5. Model Evaluation
- Evaluated models using the ROC-AUC score on both training and testing datasets.
- Visualized the confusion matrix for the XGBoost Classifier.

## Results
- All models were evaluated for their accuracy and performance using the ROC-AUC metric.
- Confusion matrix visualizations provided insights into model performance on the test dataset.

## How to Run
1. Install the required Python libraries:
   ```bash
   pip install numpy pandas matplotlib seaborn xgboost scikit-learn
   ```
2. Run the Python script in your preferred IDE or Jupyter Notebook.
3. Ensure the dataset (`new_file.csv`) is in the same directory as the script.

## File Structure
- `new_file.csv`: Dataset file containing transaction records.
- `script.py`: Python script for fraud detection analysis and modeling.

## Dependencies
- Python 3.x
- Required libraries as listed above.
