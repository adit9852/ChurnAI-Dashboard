import pandas as pd

class RiskScorer:
    def __init__(self, df):
        self.df = df

    def calculate_risk_score(self):
        """Calculate customer risk score (0-100)"""
        risk_factors = {
            'tenure_risk': 100 - (self.df['Tenure'] / self.df['Tenure'].max() * 100),
            'satisfaction_risk': 100 - (self.df['SatisfactionScore'] / 5 * 100),
            'contract_risk': self.df['ContractType'].map({
                'Month-to-Month': 100,
                'One Year': 50,
                'Two Year': 25
            }),
            'payment_risk': self.df['PaymentMethod'].map({
                'Electronic check': 80,
                'Mailed check': 60,
                'Bank transfer (automatic)': 40,
                'Credit card (automatic)': 40
            })
        }

        weights = {
            'tenure_risk': 0.3,
            'satisfaction_risk': 0.3,
            'contract_risk': 0.2,
            'payment_risk': 0.2
        }

        risk_score = sum(risk_factors[factor] * weights[factor] for factor in risk_factors)
        return risk_score

    def get_risk_categories(self):
        """Categorize customers by risk level"""
        risk_scores = self.calculate_risk_score()
        risk_categories = pd.cut(
            risk_scores,
            bins=[0, 30, 60, 100],
            labels=['Low Risk', 'Medium Risk', 'High Risk']
        )
        return risk_categories
