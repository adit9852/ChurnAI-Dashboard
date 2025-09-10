from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class ChurnPredictor:
    def __init__(self, n_estimators=100, max_depth=10):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            class_weight='balanced'  # Add class weight for imbalanced data
        )
        self.feature_importance = None

    def train(self, X, y):
        try:
            # Split the data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            # Train the model
            self.model.fit(X_train, y_train)

            # Make predictions
            y_pred = self.model.predict(X_test)
            y_prob = self.model.predict_proba(X_test)

            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'classification_report': classification_report(y_test, y_pred, output_dict=True),
                'confusion_matrix': confusion_matrix(y_test, y_pred),
                'feature_importance': self.model.feature_importances_,
                'cv_scores': cross_val_score(self.model, X, y, cv=5),
                'test_data': {
                    'y_true': y_test,
                    'y_pred': y_pred,
                    'y_prob': y_prob
                }
            }

            # Store feature importance
            self.feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)

            return metrics

        except Exception as e:
            logger.error(f"Error in model training: {str(e)}")
            raise

    def predict(self, X):
        """Return probability predictions"""
        try:
            return self.model.predict_proba(X)
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            raise

    def get_top_features(self, n=10):
        """Return top n important features"""
        if self.feature_importance is None:
            raise ValueError("Model hasn't been trained yet")
        return self.feature_importance.head(n)
