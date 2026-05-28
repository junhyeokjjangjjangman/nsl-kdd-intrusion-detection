import os
import pandas as pd
import numpy as np
import matplotlib             # 1. matplotlib를 먼저 불러오고
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay
)
def run_ids_pipeline():
# Create outputs directory if it does not exist
    os.makedirs("outputs", exist_ok=True)

    # NSL-KDD column names
    columns = [
        'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
        'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins',
        'logged_in', 'num_compromised', 'root_shell', 'su_attempted',
        'num_root', 'num_file_creations', 'num_shells', 'num_access_files',
        'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count',
        'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate',
        'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
        'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
        'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
        'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate',
        'dst_host_serror_rate', 'dst_host_srv_serror_rate',
        'dst_host_rerror_rate', 'dst_host_srv_rerror_rate',
        'label', 'difficulty'
    ]

    # Load datasets
    train_df = pd.read_csv("data/KDDTrain+.txt", header=None, names=columns)
    test_df = pd.read_csv("data/KDDTest+.txt", header=None, names=columns)

    print("========== Dataset Shape ==========")
    print("Train shape:", train_df.shape)
    print("Test shape:", test_df.shape)

    print("\n========== Dirty Data Check ==========")
    print("Train missing values:", train_df.isnull().sum().sum())
    print("Test missing values:", test_df.isnull().sum().sum())
    print("Train duplicated rows:", train_df.duplicated().sum())
    print("Test duplicated rows:", test_df.duplicated().sum())

    print("\n========== Extreme Value / Scale Check ==========")

    extreme_cols = ['duration', 'src_bytes', 'dst_bytes', 'count', 'srv_count']

    for col in extreme_cols:
        print(f"\n[{col}]")
        print("min:", train_df[col].min())
        print("max:", train_df[col].max())
        print("mean:", train_df[col].mean())
        print("median:", train_df[col].median())
        print("99% quantile:", train_df[col].quantile(0.99))

    print("\n========== IQR-based Outlier Count ==========")

    for col in extreme_cols:
        Q1 = train_df[col].quantile(0.25)
        Q3 = train_df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outlier_count = ((train_df[col] < lower_bound) | (train_df[col] > upper_bound)).sum()

        print(f"{col}: {outlier_count} outliers")

    print("\n========== Original Label Distribution ==========")
    print(train_df['label'].value_counts())

    # Binary label mapping
    # normal -> 0
    # attack -> 1
    train_df['binary_label'] = train_df['label'].apply(lambda x: 0 if x == 'normal' else 1)
    test_df['binary_label'] = test_df['label'].apply(lambda x: 0 if x == 'normal' else 1)

    print("\n========== Binary Label Distribution ==========")
    print("Train:")
    print(train_df['binary_label'].value_counts())

    print("\nTest:")
    print(test_df['binary_label'].value_counts())

    # Split features and target
    X_train = train_df.drop(columns=['label', 'difficulty', 'binary_label'])
    y_train = train_df['binary_label']

    X_test = test_df.drop(columns=['label', 'difficulty', 'binary_label'])
    y_test = test_df['binary_label']

    # Define categorical and numerical columns
    categorical_cols = ['protocol_type', 'service', 'flag']
    numerical_cols = [col for col in X_train.columns if col not in categorical_cols]

    print("\n========== Feature Type Summary ==========")
    print("Categorical columns:", categorical_cols)
    print("Number of numerical columns:", len(numerical_cols))

    # Numeric preprocessing:
    # 1. Fill missing values with median
    # 2. Apply StandardScaler
    numeric_transformer = Pipeline(
        steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]
    )

    # Categorical preprocessing:
    # 1. Fill missing values with most frequent value
    # 2. Apply One-Hot Encoding
    categorical_transformer = Pipeline(
        steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore'))
        ]
    )

    # Combine preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numerical_cols),
            ('cat', categorical_transformer, categorical_cols)
        ]
    )

    # ==============================
    # Decision Tree Parameter Experiments
    # ==============================

    experiment_results = []

    criteria = ['gini', 'entropy']
    max_depth_values = [3, 5, 10, 15, 20, None]

    best_model = None
    best_f1 = 0
    best_info = None
    best_y_pred = None

    print("\n========== Decision Tree Parameter Experiments ==========")

    for criterion in criteria:
        for max_depth in max_depth_values:

            model = Pipeline(
                steps=[
                    ('preprocessor', preprocessor),
                    ('classifier', DecisionTreeClassifier(
                        criterion=criterion,
                        max_depth=max_depth,
                        random_state=42
                    ))
                ]
            )

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)

            experiment_results.append({
                'Model': 'Decision Tree',
                'Criterion': criterion,
                'Max Depth': str(max_depth),
                'Accuracy': accuracy,
                'Precision': precision,
                'Recall': recall,
                'F1-score': f1
            })

            print(f"criterion={criterion}, max_depth={max_depth}")
            print(f"Accuracy={accuracy:.4f}, Precision={precision:.4f}, Recall={recall:.4f}, F1-score={f1:.4f}")
            print("-" * 70)

            if f1 > best_f1:
                best_f1 = f1
                best_model = model
                best_info = {
                    'criterion': criterion,
                    'max_depth': max_depth,
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1
                }
                best_y_pred = y_pred

    # Save experiment result table
    result_df = pd.DataFrame(experiment_results)
    result_df.to_csv("outputs/decision_tree_experiment_results.csv", index=False)

    print("\n========== Best Model ==========")
    print(best_info)

    print("\n========== Best Model Classification Report ==========")
    print(classification_report(y_test, best_y_pred, target_names=['Normal', 'Attack']))

    # Best model confusion matrix
    cm = confusion_matrix(y_test, best_y_pred)

    print("\n========== Best Model Confusion Matrix ==========")
    print(cm)

    # ==============================
    # K-Fold Cross Validation
    # ==============================

    print("\n========== 5-Fold Cross Validation ==========")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    cv_model = Pipeline(
        steps=[
            ('preprocessor', preprocessor),
            ('classifier', DecisionTreeClassifier(
                criterion=best_info['criterion'],
                max_depth=best_info['max_depth'],
                random_state=42
            ))
        ]
    )

    cv_scores = cross_val_score(
        cv_model,
        X_train,
        y_train,
        cv=cv,
        scoring='f1'
    )

    cv_result_df = pd.DataFrame({
        'Fold': [1, 2, 3, 4, 5],
        'F1-score': cv_scores
    })

    cv_result_df.loc[len(cv_result_df)] = ['Mean', cv_scores.mean()]
    cv_result_df.loc[len(cv_result_df)] = ['Std', cv_scores.std()]

    cv_result_df.to_csv("outputs/cross_validation_results.csv", index=False)

    print(cv_result_df)
    print("Saved: outputs/cross_validation_results.csv")

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=['Normal', 'Attack']
    )

    disp.plot()
    plt.title("Confusion Matrix - Best Decision Tree")
    plt.savefig("outputs/confusion_matrix_best_decision_tree.png", dpi=300, bbox_inches='tight')
    plt.close()

    print("\n========== Saved Outputs ==========")
    print("outputs/decision_tree_experiment_results.csv")
    print("outputs/confusion_matrix_best_decision_tree.png")

    # ==============================
    # Feature Importance
    # ==============================

    print("\n========== Feature Importance ==========")

    # Fit the best model again to make sure it is trained
    best_model.fit(X_train, y_train)

    # Get trained classifier and preprocessor
    classifier = best_model.named_steps['classifier']
    preprocessor_fitted = best_model.named_steps['preprocessor']

    # Get numerical feature names
    num_features = numerical_cols

    # Get one-hot encoded categorical feature names
    cat_features = preprocessor_fitted.named_transformers_['cat'] \
        .named_steps['encoder'] \
        .get_feature_names_out(categorical_cols)

    # Combine all transformed feature names
    all_feature_names = list(num_features) + list(cat_features)

    # Create feature importance table
    feature_importance_df = pd.DataFrame({
        'Feature': all_feature_names,
        'Importance': classifier.feature_importances_
    })

    feature_importance_df = feature_importance_df.sort_values(
        by='Importance',
        ascending=False
    )

    # Save full feature importance result
    feature_importance_df.to_csv("outputs/feature_importance.csv", index=False)

    # Save top 20 feature importance plot
    top20 = feature_importance_df.head(20)

    plt.figure(figsize=(10, 6))
    plt.barh(top20['Feature'][::-1], top20['Importance'][::-1])
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title("Top 20 Feature Importance - Decision Tree")
    plt.tight_layout()
    plt.savefig("outputs/feature_importance_top20.png", dpi=300, bbox_inches='tight')
    plt.close()

    print(top20)
    print("Saved: outputs/feature_importance.csv")
    print("Saved: outputs/feature_importance_top20.png")
    print("All pipeLine and result save")


if __name__ == "__main__":
    run_ids_pipeline()