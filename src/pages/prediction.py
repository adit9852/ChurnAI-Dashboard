import streamlit as st
import pandas as pd
from src.model import ChurnPredictor
import plotly.graph_objects as go

def render_prediction_page(df, data_processor):
    st.subheader("🤖 Churn Prediction System")

    # Model Configuration
    st.sidebar.subheader("Model Parameters")
    n_estimators = st.sidebar.slider("Number of trees", 50, 300, 100)
    max_depth = st.sidebar.slider("Max depth", 3, 20, 10)

    # Prepare data and train model
    X, y = data_processor.prepare_model_data()
    predictor = ChurnPredictor(n_estimators=n_estimators, max_depth=max_depth)
    metrics = predictor.train(X, y)

    # Model Performance Metrics
    st.subheader("Model Performance")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Accuracy",
            f"{metrics['accuracy']:.2%}",
            f"{(metrics['accuracy'] - 0.5):.2%} vs baseline"
        )

    with col2:
        precision = metrics['classification_report']['1']['precision']
        st.metric("Precision", f"{precision:.2%}")

    with col3:
        recall = metrics['classification_report']['1']['recall']
        st.metric("Recall", f"{recall:.2%}")

    # Confusion Matrix
    st.subheader("Confusion Matrix")
    conf_matrix = metrics['confusion_matrix']
    fig = go.Figure(data=go.Heatmap(
        z=conf_matrix,
        x=['Predicted No Churn', 'Predicted Churn'],
        y=['Actual No Churn', 'Actual Churn'],
        colorscale='RdYlGn'
    ))
    st.plotly_chart(fig, use_container_width=True)

    # Feature Importance
    st.subheader("Feature Importance")
    importance_df = pd.DataFrame({
        'feature': X.columns,
        'importance': metrics['feature_importance']
    }).sort_values('importance', ascending=False)

    fig = go.Figure(go.Bar(
        x=importance_df['importance'][:10],
        y=importance_df['feature'][:10],
        orientation='h'
    ))
    st.plotly_chart(fig, use_container_width=True)

    # Interactive Prediction System
    st.subheader("Interactive Prediction System")
    st.write("Use this system to predict churn probability for a customer")

    col1, col2, col3 = st.columns(3)

    with col1:
        tenure = st.slider("Tenure (months)", 0, 72, 24)
        monthly_charges = st.slider("Monthly Charges ($)",
                                  float(df['MonthlyCharges'].min()),
                                  float(df['MonthlyCharges'].max()),
                                  70.0)
        satisfaction = st.slider("Satisfaction Score", 1.0, 5.0, 3.5)

    with col2:
        contract = st.selectbox("Contract Type", df['ContractType'].unique())
        internet = st.selectbox("Internet Service", df['InternetService'].unique())
        payment = st.selectbox("Payment Method", df['PaymentMethod'].unique())

    with col3:
        streaming_tv = st.selectbox("Streaming TV", ['Yes', 'No'])
        streaming_movies = st.selectbox("Streaming Movies", ['Yes', 'No'])
        phone = st.selectbox("Phone Service", ['Yes', 'No'])

    if st.button("Predict Churn Probability"):
        # Create test customer data
        test_customer = pd.DataFrame({
            'Tenure': [tenure],
            'MonthlyCharges': [monthly_charges],
            'SatisfactionScore': [satisfaction],
            'ContractType': [contract],
            'InternetService': [internet],
            'PaymentMethod': [payment],
            'StreamingTV': [streaming_tv],
            'StreamingMovies': [streaming_movies],
            'PhoneService': [phone]
        })

        # Process test data
        test_customer_processed = pd.get_dummies(test_customer)
        test_customer_processed = test_customer_processed.reindex(columns=X.columns, fill_value=0)

        # Make prediction
        churn_prob = predictor.predict(test_customer_processed)[0][1]

        # Display prediction gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=churn_prob * 100,
            title={'text': "Churn Probability (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 30], 'color': "green"},
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
        st.plotly_chart(fig, use_container_width=True)

        # Risk assessment and recommendations
        st.subheader("Risk Assessment and Recommendations")

        if churn_prob > 0.7:
            st.error("⚠️ High Risk of Churn")
            st.write("Immediate Actions Recommended:")
            st.write("1. Schedule immediate customer contact")
            st.write("2. Offer personalized retention package")
            st.write("3. Consider contract upgrade incentives")
            st.write("4. Conduct service quality review")

        elif churn_prob > 0.3:
            st.warning("🔔 Moderate Risk of Churn")
            st.write("Recommended Actions:")
            st.write("1. Proactive customer engagement")
            st.write("2. Review service usage patterns")
            st.write("3. Consider loyalty rewards")

        else:
            st.success("✅ Low Risk of Churn")
            st.write("Recommended Actions:")
            st.write("1. Maintain service quality")
            st.write("2. Consider upselling opportunities")
            st.write("3. Gather feedback for improvement")

        # Similar Customer Analysis
        st.subheader("Similar Customer Analysis")

        # Find similar customers based on key features
        similar_customers = df[
            (df['ContractType'] == contract) &
            (df['MonthlyCharges'].between(monthly_charges*0.8, monthly_charges*1.2)) &
            (df['Tenure'].between(max(0, tenure-6), tenure+6))
        ]

        st.write(f"Found {len(similar_customers)} similar customers")
        st.write(f"Historical churn rate for similar customers: {similar_customers['Churn'].mean():.1%}")

        # Export prediction results
        if st.button("Export Prediction Report"):
            prediction_report = pd.DataFrame({
                'Feature': test_customer.columns,
                'Value': test_customer.iloc[0]
            })

            prediction_report.to_excel('prediction_report.xlsx', index=False)

            with open('prediction_report.xlsx', 'rb') as f:
                st.download_button(
                    label="Download Prediction Report",
                    data=f,
                    file_name="prediction_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
