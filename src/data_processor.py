import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, df):
        self.df = df
        self.scaler = StandardScaler()
        self.label_encoders = {}

    def prepare_model_data(self, target_col='Churn'):
        try:
            # Create a copy of the dataframe
            model_df = self.df.copy()

            # Drop non-predictive columns
            cols_to_drop = ['CustomerID', 'LastUpdate']
            model_df = model_df.drop(cols_to_drop, axis=1, errors='ignore')

            # Handle categorical variables
            categorical_cols = model_df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                self.label_encoders[col] = LabelEncoder()
                model_df[col] = self.label_encoders[col].fit_transform(model_df[col])

            # Separate features and target
            X = model_df.drop([target_col], axis=1)
            y = model_df[target_col]

            # Scale numerical features
            numerical_cols = X.select_dtypes(include=['float64', 'int64']).columns
            X[numerical_cols] = self.scaler.fit_transform(X[numerical_cols])

            return X, y

        except Exception as e:
            logger.error(f"Error in data preparation: {str(e)}")
            raise

    def calculate_customer_metrics(self):
        """Calculate additional customer metrics"""
        try:
            # Calculate Customer Lifetime Value
            self.df['CLV'] = self.df['MonthlyCharges'] * self.df['Tenure']

            # Calculate Average Revenue Per User (ARPU)
            self.df['ARPU'] = self.df['TotalCharges'] / self.df['Tenure'].clip(1)

            # Calculate Service Usage Score
            service_cols = ['PhoneService', 'InternetService', 'StreamingTV', 'StreamingMovies']
            self.df['ServiceUsageScore'] = self.df[service_cols].apply(
                lambda x: sum(x != 'No'), axis=1
            )

            return self.df

        except Exception as e:
            logger.error(f"Error calculating customer metrics: {str(e)}")
            raise

    def get_feature_importance(self, model, X):
        """Get feature importance from the model"""
        try:
            importance = pd.DataFrame({
                'feature': X.columns,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)

            return importance

        except Exception as e:
            logger.error(f"Error calculating feature importance: {str(e)}")
            raise
