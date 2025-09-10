import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from src.analytics.clv_analyzer import CLVAnalyzer
from src.analytics.risk_scorer import RiskScorer
from src.analytics.engagement_analyzer import EngagementAnalyzer
from src.analytics.recommendation_engine import RecommendationEngine

def render_advanced_analytics_page(df):
    st.subheader("🔬 Advanced Analytics Dashboard")

    # Initialize analytics components
    clv_analyzer = CLVAnalyzer(df)
    risk_scorer = RiskScorer(df)
    engagement_analyzer = EngagementAnalyzer(df)
    recommendation_engine = RecommendationEngine(df)

    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "Customer Lifetime Value",
        "Risk Analysis",
        "Engagement Metrics",
        "Recommendations"
    ])

    with tab1:
        render_clv_analysis(df, clv_analyzer)

    with tab2:
        render_risk_analysis(df, risk_scorer)

    with tab3:
        render_engagement_analysis(df, engagement_analyzer)

    with tab4:
        render_recommendations(df, recommendation_engine)

def render_clv_analysis(df, clv_analyzer):
    st.subheader("Customer Lifetime Value Analysis")

    # Calculate CLV metrics
    df['CLV'] = clv_analyzer.calculate_basic_clv()
    df['PredictedCLV'] = clv_analyzer.calculate_predicted_clv()
    value_segments = clv_analyzer.segment_value_analysis()

    col1, col2 = st.columns(2)

    with col1:
        # CLV Distribution
        fig = px.histogram(
            df,
            x='CLV',
            color='Churn',
            marginal='box',
            title='Customer Lifetime Value Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Value Segment Analysis
        fig = px.bar(
            value_segments.reset_index(),
            x='ValueSegment',
            y='TotalCharges',
            title='Revenue by Value Segment',
            color='Churn'
        )
        st.plotly_chart(fig, use_container_width=True)

    # CLV Predictions
    st.subheader("CLV Predictions")
    col1, col2 = st.columns(2)

    with col1:
        fig = px.scatter(
            df,
            x='CLV',
            y='PredictedCLV',
            color='ContractType',
            title='Current vs Predicted CLV',
            trendline="ols"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Top Value Customers
        top_customers = df.nlargest(10, 'CLV')[
            ['CustomerID', 'CLV', 'PredictedCLV', 'ContractType']
        ]
        st.write("Top 10 Customers by CLV")
        st.dataframe(top_customers)

def render_risk_analysis(df, risk_scorer):
    st.subheader("Risk Analysis")

    # Calculate risk scores
    df['RiskScore'] = risk_scorer.calculate_risk_score()
    df['RiskCategory'] = risk_scorer.get_risk_categories()

    col1, col2 = st.columns(2)

    with col1:
        # Risk Score Distribution
        fig = px.histogram(
            df,
            x='RiskScore',
            color='RiskCategory',
            title='Risk Score Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Risk by Contract Type
        risk_by_contract = df.groupby('ContractType')['RiskScore'].mean().reset_index()
        fig = px.bar(
            risk_by_contract,
            x='ContractType',
            y='RiskScore',
            title='Average Risk Score by Contract Type',
            color='RiskScore',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Risk Factors Analysis
    st.subheader("Risk Factors Analysis")
    risk_factors = pd.DataFrame({
        'Factor': ['Tenure', 'Satisfaction', 'Contract', 'Payment'],
        'Impact': [0.3, 0.3, 0.2, 0.2]
    })
    fig = px.pie(
        risk_factors,
        values='Impact',
        names='Factor',
        title='Risk Factor Weights'
    )
    st.plotly_chart(fig, use_container_width=True)

    # High Risk Customers
    high_risk = df[df['RiskCategory'] == 'High Risk'].sort_values('RiskScore', ascending=False)
    st.write("High Risk Customers")
    st.dataframe(high_risk[['CustomerID', 'RiskScore', 'MonthlyCharges', 'Tenure', 'ContractType']])

def render_engagement_analysis(df, engagement_analyzer):
    st.subheader("Customer Engagement Analysis")

    # Calculate engagement metrics
    df['EngagementScore'] = engagement_analyzer.calculate_engagement_score()
    engagement_insights = engagement_analyzer.get_engagement_insights()

    col1, col2 = st.columns(2)

    with col1:
        # Engagement Score Distribution
        fig = px.histogram(
            df,
            x='EngagementScore',
            color='Churn',
            title='Engagement Score Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Service Adoption Analysis
        service_adoption = engagement_analyzer.calculate_service_adoption()
        fig = px.box(
            df,
            x='ContractType',
            y=service_adoption,
            color='Churn',
            title='Service Adoption by Contract Type'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Engagement Trends
    st.subheader("Engagement Trends")
    engagement_by_tenure = df.groupby(pd.qcut(df['Tenure'], 4))['EngagementScore'].mean()
    fig = px.line(
        x=engagement_by_tenure.index.astype(str),
        y=engagement_by_tenure.values,
        title='Engagement Score by Tenure',
        labels={'x': 'Tenure Quartile', 'y': 'Average Engagement Score'}
    )
    st.plotly_chart(fig, use_container_width=True)

def render_recommendations(df, recommendation_engine):
    st.subheader("Recommendation System")

    # Customer-specific recommendations
    customer_id = st.selectbox(
        "Select Customer ID",
        options=df['CustomerID'].unique()
    )

    if customer_id:
        recommendations = recommendation_engine.get_personalized_recommendations(customer_id)
        st.write("### Personal Recommendations")
        for rec in recommendations:
            if rec['priority'] == 'High':
                st.error(f"🔴 {rec['type']}: {rec['description']}")
            elif rec['priority'] == 'Medium':
                st.warning(f"🟡 {rec['type']}: {rec['description']}")
            else:
                st.info(f"🟢 {rec['type']}: {rec['description']}")

    # Segment by Contract Type instead of undefined segments
    st.write("### Contract Type Recommendations")
    for contract_type in df['ContractType'].unique():
        st.write(f"#### {contract_type} Customers")

        # Create segment-specific metrics
        segment_data = df[df['ContractType'] == contract_type]
        churn_rate = segment_data['Churn'].mean()
        avg_satisfaction = segment_data['SatisfactionScore'].mean()
        avg_tenure = segment_data['Tenure'].mean()

        # Display segment metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Churn Rate", f"{churn_rate:.1%}")
        with col2:
            st.metric("Avg Satisfaction", f"{avg_satisfaction:.1f}")
        with col3:
            st.metric("Avg Tenure", f"{avg_tenure:.1f} months")

        # Generate recommendations based on metrics
        if churn_rate > 0.3:
            st.error("🔴 High churn rate detected - Implement retention program")
        if avg_satisfaction < 3.5:
            st.warning("🟡 Low satisfaction score - Review service quality")
        if avg_tenure < 12:
            st.info("🟢 New customer segment - Focus on engagement")

    # Export functionality
    if st.button("Export Analytics Report"):
        with pd.ExcelWriter('advanced_analytics_report.xlsx', engine='xlsxwriter') as output:
            # Export CLV analysis
            df[['CustomerID', 'CLV', 'PredictedCLV', 'RiskScore', 'RiskCategory', 'EngagementScore']].to_excel(
                output, sheet_name='Customer_Metrics', index=False
            )

            # Export contract type analysis
            contract_analysis = df.groupby('ContractType').agg({
                'Churn': 'mean',
                'SatisfactionScore': 'mean',
                'Tenure': 'mean',
                'MonthlyCharges': 'mean'
            }).round(2)
            contract_analysis.to_excel(output, sheet_name='Contract_Analysis')

        with open('advanced_analytics_report.xlsx', 'rb') as f:
            st.download_button(
                label="📥 Download Analytics Report",
                data=f,
                file_name="advanced_analytics_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
