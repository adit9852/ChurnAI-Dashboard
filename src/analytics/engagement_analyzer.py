import pandas as pd

class EngagementAnalyzer:
    def __init__(self, df):
        self.df = df

    def calculate_engagement_score(self):
        """Calculate customer engagement score"""
        # Service adoption score
        service_columns = ['PhoneService', 'InternetService', 'StreamingTV', 'StreamingMovies']
        service_score = self.df[service_columns].apply(
            lambda x: sum(x != 'No'), axis=1
        ) / len(service_columns) * 100

        # Tenure score
        tenure_score = self.df['Tenure'] / self.df['Tenure'].max() * 100

        # Contract commitment score
        contract_score = self.df['ContractType'].map({
            'Month-to-Month': 33,
            'One Year': 66,
            'Two Year': 100
        })

        # Combined engagement score
        engagement_score = (service_score * 0.4 + tenure_score * 0.3 + contract_score * 0.3)
        return engagement_score

    def get_engagement_insights(self):
        """Get detailed engagement insights"""
        engagement_score = self.calculate_engagement_score()

        insights = pd.DataFrame({
            'EngagementScore': engagement_score,
            'ServiceAdoption': self.calculate_service_adoption(),
            'ContractCommitment': self.df['ContractType'].map({
                'Month-to-Month': 'Low',
                'One Year': 'Medium',
                'Two Year': 'High'
            }),
            'Tenure': self.df['Tenure']
        })

        return insights

    def calculate_service_adoption(self):
        """Calculate service adoption rate"""
        service_columns = ['PhoneService', 'InternetService', 'StreamingTV', 'StreamingMovies']
        return self.df[service_columns].apply(
            lambda x: sum(x != 'No'), axis=1
        ) / len(service_columns)
