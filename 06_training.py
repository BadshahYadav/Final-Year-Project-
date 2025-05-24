import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

# Load the dataset
def load_data(csv_file):
    data = pd.read_csv(csv_file)
    
    # Handle missing values (if any)
    if data.isnull().sum().any():
        print("[!] Missing values found. Filling missing values with the column mean.")
        data.fillna(data.mean(), inplace=True)  # Simple strategy to fill missing values
    
    X = data.drop('label', axis=1)  # Features
    y = data['label']  # Labels
    return X, y

# Train the classifier
def train_classifier(X_train, y_train):
    classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    classifier.fit(X_train, y_train)
    return classifier

# Evaluate the classifier
def evaluate_classifier(classifier, X_test, y_test):
    y_pred = classifier.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='binary')
    recall = recall_score(y_test, y_pred, average='binary')
    f1 = f1_score(y_test, y_pred, average='binary')

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-score: {f1:.4f}")
    
    # Display confusion matrix for better insight
    cm = confusion_matrix(y_test, y_pred)
    print(f"Confusion Matrix:\n{cm}")

# Main function to train and evaluate the model
if __name__ == "__main__":
    # Load the dataset
    X, y = load_data("dataset.csv")

    # Split the data into train and test sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Train the classifier
    classifier = train_classifier(X_train, y_train)

    # Evaluate the classifier
    evaluate_classifier(classifier, X_test, y_test)

    # Save the trained model for future use
    joblib.dump(classifier, "malware_classifier.pkl")
    print("[✓] Model saved as 'malware_classifier.pkl'")
