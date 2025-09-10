class RecommendationEngine:
    def __init__(self, df):
        self.df = df

    def get_personalized_recommendations(self, customer_id):
        """Generate personalized recommendations for a customer"""
        customer = self.df[self.df['CustomerID'] == customer_id].iloc[0]
        recommendations = []

        # Contract upgrade recommendations
        if customer['ContractType'] == 'Month-to-Month':
            recommendations.append({
                'type': 'Contract Upgrade',
                'description': 'Consider upgrading to an annual contract for better rates',
                'priority': 'High' if customer['MonthlyCharges'] > 70 else 'Medium'
            })

        # Service recommendations
        if customer['InternetService'] != 'No':
            if customer['StreamingTV'] == 'No':
                recommendations.append({
                    'type': 'Service Addition',
                    'description': 'Add StreamingTV service to your package',
                    'priority': 'Medium'
                })
            if customer['StreamingMovies'] == 'No':
                recommendations.append({
                    'type': 'Service Addition',
                    'description': 'Add StreamingMovies service to your package',
                    'priority': 'Medium'
                })

        # Retention recommendations
        if customer['SatisfactionScore'] < 3:
            recommendations.append({
                'type': 'Retention',
                'description': 'Schedule customer satisfaction review',
                'priority': 'High'
            })

        return recommendations

    def get_segment_recommendations(self, segment):
        """Generate segment-level recommendations"""
        segment_data = self.df[self.df['Segment'] == segment]

        avg_satisfaction = segment_data['SatisfactionScore'].mean()
        churn_rate = segment_data['Churn'].mean()
        avg_tenure = segment_data['Tenure'].mean()

        recommendations = []

        if churn_rate > 0.3:
            recommendations.append({
                'type': 'Retention',
                'description': 'Implement targeted retention program',
                'priority': 'High'
            })

        if avg_satisfaction < 3.5:
            recommendations.append({
                'type': 'Satisfaction',
                'description': 'Launch satisfaction improvement initiative',
                'priority': 'High'
            })

        if avg_tenure < 12:
            recommendations.append({
                'type': 'Engagement',
                'description': 'Develop early-stage engagement program',
                'priority': 'Medium'
            })

        return recommendations
