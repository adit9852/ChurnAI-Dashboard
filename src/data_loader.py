import pandas as pd
import numpy as np
import streamlit as st
from src.config import config
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    @staticmethod
    def transform_telco_data(df):
        """Transform IBM Telco data to match our schema"""
        df_transformed = df.copy()

        # 1. Rename columns
        column_mapping = {
            'customerID': 'CustomerID',
            'gender': 'Gender',
            'tenure': 'Tenure',
            'Contract': 'ContractType'
        }
        df_transformed.rename(columns=column_mapping, inplace=True)

        # 2. Convert TotalCharges to numeric
        df_transformed['TotalCharges'] = pd.to_numeric(df_transformed['TotalCharges'], errors='coerce')
        df_transformed['TotalCharges'].fillna(df_transformed['MonthlyCharges'] * df_transformed['Tenure'], inplace=True)

        # 3. Standardize ContractType values
        contract_mapping = {
            'Month-to-month': 'Month-to-Month',
            'One year': 'One Year',
            'Two year': 'Two Year'
        }
        df_transformed['ContractType'] = df_transformed['ContractType'].map(contract_mapping)

        # 4. Convert Churn to numeric
        df_transformed['Churn'] = (df_transformed['Churn'] == 'Yes').astype(int)

        # 5. Generate synthetic Age (based on reasonable assumptions)
        np.random.seed(42)  # for reproducibility
        df_transformed['Age'] = np.random.normal(45, 15, size=len(df_transformed))
        df_transformed['Age'] = df_transformed['Age'].clip(18, 85).astype(int)

        # 6. Generate synthetic SatisfactionScore
        # Higher for non-churned customers, lower for churned ones
        df_transformed['SatisfactionScore'] = 5 - (df_transformed['Churn'] * 2) + \
            np.random.normal(0, 0.5, size=len(df_transformed))
        df_transformed['SatisfactionScore'] = df_transformed['SatisfactionScore'].clip(1, 5).round(1)

        # 7. Add LastUpdate column for time-based analysis
        dates = pd.date_range(
            end=pd.Timestamp.now(),
            periods=len(df_transformed),
            freq='D'
        )
        df_transformed['LastUpdate'] = dates[np.random.permutation(len(dates))]

        return df_transformed

    @st.cache_data(show_spinner=True)
    def load_data():
        try:
            with st.spinner('Loading data...'):
                # Load the raw IBM Telco data
                df = pd.read_csv(config.data_path)

                # Transform to match our schema
                df_transformed = DataLoader.transform_telco_data(df)

                logger.info("Data loaded and transformed successfully")
                return df_transformed

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            st.error(f"Error loading data: {str(e)}")
            return None
