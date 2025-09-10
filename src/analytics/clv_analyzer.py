import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class CLVAnalyzer:
    def __init__(self, df):
        self.df = df

    def calculate_basic_clv(self):
        """Calculate basic Customer Lifetime Value"""
        self.df['CLV'] = self.df['MonthlyCharges'] * self.df['Tenure']
        return self.df['CLV']

    def calculate_predicted_clv(self, prediction_months=12):
        """Calculate predicted CLV using linear regression"""
        # Prepare features for prediction
        features = ['Tenure', 'MonthlyCharges', 'SatisfactionScore']
        X = self.df[features]
        y = self.df['TotalCharges']

        # Train linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Create future scenario
        future_df = self.df.copy()
        future_df['Tenure'] = future_df['Tenure'] + prediction_months

        # Predict future total charges
        future_charges = model.predict(future_df[features])

        return pd.Series(future_charges - self.df['TotalCharges'], name='PredictedAdditionalCLV')

    def segment_value_analysis(self):
        """Analyze customer value segments"""
        self.df['ValueSegment'] = pd.qcut(self.df['TotalCharges'], q=4, labels=['Bronze', 'Silver', 'Gold', 'Platinum'])
        return self.df.groupby('ValueSegment').agg({
            'MonthlyCharges': 'mean',
            'Tenure': 'mean',
            'Churn': 'mean',
            'TotalCharges': 'sum'
        })
