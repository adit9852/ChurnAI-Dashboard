import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from src.config import config

class Visualizer:
    def __init__(self, df):
        self.df = df
        try:
            self.color_scheme = config.config.get('visualization', {}).get(
                'color_scheme',
                ["#2ecc71", "#e74c3c", "#3498db"]
            )
            self.chart_theme = config.config.get('visualization', {}).get(
                'chart_theme',
                "plotly_white"
            )
            self.categorical_palette = config.config.get('visualization', {}).get(
                'categorical_palette',
                "Set3"
            )
            self.correlation_colorscale = config.config.get('visualization', {}).get(
                'correlation_colorscale',
                "RdBu"
            )
        except Exception as e:
            print(f"Warning: Using default visualization settings. Error: {e}")
            self.color_scheme = ["#2ecc71", "#e74c3c", "#3498db"]
            self.chart_theme = "plotly_white"
            self.categorical_palette = "Set3"
            self.correlation_colorscale = "RdBu"

    def plot_churn_distribution(self):
        """Plot overall churn distribution"""
        churn_counts = self.df['Churn'].value_counts()
        fig = go.Figure(data=[
            go.Pie(
                labels=['Retained', 'Churned'],
                values=churn_counts.values,
                hole=0.4,
                marker_colors=['#2ecc71', '#e74c3c']
            )
        ])
        fig.update_layout(
            title='Customer Churn Distribution',
            annotations=[dict(text=f'Total: {len(self.df)}', x=0.5, y=0.5, font_size=15, showarrow=False)]
        )
        return fig

    def plot_contract_churn(self):
        """Plot churn by contract type"""
        contract_churn = pd.crosstab(self.df['ContractType'], self.df['Churn'])
        fig = go.Figure(data=[
            go.Bar(
                name='Retained',
                x=contract_churn.index,
                y=contract_churn[0],
                marker_color='#2ecc71'
            ),
            go.Bar(
                name='Churned',
                x=contract_churn.index,
                y=contract_churn[1],
                marker_color='#e74c3c'
            )
        ])
        fig.update_layout(
            barmode='group',
            title='Churn by Contract Type',
            xaxis_title='Contract Type',
            yaxis_title='Number of Customers'
        )
        return fig

    def plot_monthly_charges_distribution(self):
        """Plot monthly charges distribution by churn"""
        fig = ff.create_distplot(
            [
                self.df[self.df['Churn'] == 0]['MonthlyCharges'],
                self.df[self.df['Churn'] == 1]['MonthlyCharges']
            ],
            ['Retained', 'Churned'],
            colors=['#2ecc71', '#e74c3c']
        )
        fig.update_layout(
            title='Monthly Charges Distribution by Churn Status',
            xaxis_title='Monthly Charges ($)',
            yaxis_title='Density'
        )
        return fig

    def plot_service_usage(self):
        """Plot service usage patterns"""
        services = ['PhoneService', 'InternetService', 'StreamingTV', 'StreamingMovies']
        service_data = []

        for service in services:
            service_counts = self.df.groupby([service, 'Churn']).size().unstack()
            service_data.append(service_counts)

        fig = go.Figure()
        for i, service in enumerate(services):
            fig.add_trace(go.Bar(
                name=f'{service} - Retained',
                x=[service],
                y=[service_data[i][0].sum()],
                marker_color='#2ecc71'
            ))
            fig.add_trace(go.Bar(
                name=f'{service} - Churned',
                x=[service],
                y=[service_data[i][1].sum()],
                marker_color='#e74c3c'
            ))

        fig.update_layout(
            barmode='group',
            title='Service Usage by Churn Status',
            xaxis_title='Services',
            yaxis_title='Number of Customers'
        )
        return fig

    def plot_satisfaction_impact(self):
        """Plot satisfaction score impact on churn"""
        fig = go.Figure()

        for churn in [0, 1]:
            data = self.df[self.df['Churn'] == churn]['SatisfactionScore']
            fig.add_trace(go.Violin(
                x=['Retained' if churn == 0 else 'Churned'] * len(data),
                y=data,
                name='Retained' if churn == 0 else 'Churned',
                box_visible=True,
                meanline_visible=True,
                marker_color='#2ecc71' if churn == 0 else '#e74c3c'
            ))

        fig.update_layout(
            title='Satisfaction Score Distribution by Churn Status',
            xaxis_title='Customer Status',
            yaxis_title='Satisfaction Score'
        )
        return fig

    def plot_tenure_analysis(self):
        """Plot tenure analysis"""
        fig = go.Figure()

        # Average monthly charges by tenure for churned and retained customers
        for churn in [0, 1]:
            tenure_avg = self.df[self.df['Churn'] == churn].groupby('Tenure')['MonthlyCharges'].mean()
            fig.add_trace(go.Scatter(
                x=tenure_avg.index,
                y=tenure_avg.values,
                mode='lines+markers',
                name='Retained' if churn == 0 else 'Churned',
                marker_color='#2ecc71' if churn == 0 else '#e74c3c'
            ))

        fig.update_layout(
            title='Average Monthly Charges by Tenure',
            xaxis_title='Tenure (months)',
            yaxis_title='Average Monthly Charges ($)'
        )
        return fig

    def plot_correlation_matrix(self):
        """Plot correlation matrix for numerical features"""
        numerical_cols = ['Tenure', 'MonthlyCharges', 'TotalCharges', 'SatisfactionScore', 'Age']
        corr_matrix = self.df[numerical_cols].corr()

        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmin=-1,
            zmax=1
        ))

        fig.update_layout(
            title='Feature Correlation Matrix',
            width=700,
            height=700
        )
        return fig

    def plot_churn_prediction_gauge(self, probability):
        """Plot gauge chart for churn probability"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=probability * 100,
            title={'text': "Churn Probability"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        return fig

    def plot_feature_importance(self, importance_df, top_n=10):
        """Plot feature importance"""
        fig = go.Figure(go.Bar(
            x=importance_df['importance'][:top_n],
            y=importance_df['feature'][:top_n],
            orientation='h',
            marker_color='#3498db'
        ))

        fig.update_layout(
            title=f'Top {top_n} Most Important Features',
            xaxis_title='Importance Score',
            yaxis_title='Feature',
            height=400
        )
        return fig

    def plot_customer_segments(self, df_with_segments):
        """Plot customer segments in 3D space"""
        fig = px.scatter_3d(
            df_with_segments,
            x='MonthlyCharges',
            y='Tenure',
            z='SatisfactionScore',
            color='Segment',
            symbol='Churn',
            title='Customer Segments',
            labels={
                'MonthlyCharges': 'Monthly Charges ($)',
                'Tenure': 'Tenure (months)',
                'SatisfactionScore': 'Satisfaction Score'
            }
        )

        fig.update_layout(
            scene=dict(
                xaxis_title='Monthly Charges ($)',
                yaxis_title='Tenure (months)',
                zaxis_title='Satisfaction Score'
            )
        )
        return fig
