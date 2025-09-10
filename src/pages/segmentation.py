import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np

def render_segmentation_page(df, data_processor, visualizer):
    st.subheader("🎯 Customer Segmentation Analysis")

    # Segmentation Configuration
    st.sidebar.subheader("Segmentation Parameters")
    n_clusters = st.sidebar.slider("Number of Segments", 2, 6, 3)

    # Feature Selection for Segmentation
    st.subheader("Feature Selection")
    col1, col2 = st.columns(2)

    with col1:
        selected_features = st.multiselect(
            "Select Features for Segmentation",
            options=['Tenure', 'MonthlyCharges', 'TotalCharges', 'SatisfactionScore'],
            default=['Tenure', 'MonthlyCharges', 'SatisfactionScore']
        )

    with col2:
        scaling_method = st.selectbox(
            "Scaling Method",
            options=['Standard Scaling', 'Min-Max Scaling'],
            index=0
        )

    if len(selected_features) < 2:
        st.warning("Please select at least 2 features for segmentation")
        return

    # Prepare data for clustering
    X = df[selected_features].copy()

    # Handle missing values if any
    X = X.fillna(X.mean())

    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

    # Perform clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['Segment'] = kmeans.fit_predict(X_scaled)

    # Visualization tabs
    tab1, tab2, tab3 = st.tabs(["Segment Overview", "Detailed Analysis", "Customer Profiles"])

    with tab1:
        st.subheader("Segment Overview")

        # 3D Scatter plot if we have 3 or more features
        if len(selected_features) >= 3:
            fig = px.scatter_3d(
                df,
                x=selected_features[0],
                y=selected_features[1],
                z=selected_features[2],
                color='Segment',
                symbol='Churn',
                title='Customer Segments Visualization',
                labels={col: col.replace('_', ' ') for col in selected_features}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # 2D Scatter plot
            fig = px.scatter(
                df,
                x=selected_features[0],
                y=selected_features[1],
                color='Segment',
                symbol='Churn',
                title='Customer Segments Visualization'
            )
            st.plotly_chart(fig, use_container_width=True)

        # Segment Size Distribution
        segment_sizes = df['Segment'].value_counts()
        fig = px.pie(
            values=segment_sizes.values,
            names=segment_sizes.index,
            title='Segment Size Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Detailed Segment Analysis")

        # Feature distribution across segments
        selected_feature = st.selectbox(
            "Select feature to analyze",
            options=selected_features + ['MonthlyCharges', 'Churn']
        )

        # Box plot of selected feature across segments
        fig = px.box(
            df,
            x='Segment',
            y=selected_feature,
            color='Segment',
            title=f'{selected_feature} Distribution by Segment'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Segment characteristics table
        segment_stats = df.groupby('Segment').agg({
            'Tenure': 'mean',
            'MonthlyCharges': 'mean',
            'TotalCharges': 'mean',
            'SatisfactionScore': 'mean',
            'Churn': 'mean'
        }).round(2)

        st.write("Segment Characteristics:")
        st.dataframe(segment_stats)

        # Churn rate by segment
        fig = px.bar(
            segment_stats.reset_index(),
            x='Segment',
            y='Churn',
            title='Churn Rate by Segment',
            color='Segment'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Customer Profiles")

        for segment in range(n_clusters):
            segment_data = df[df['Segment'] == segment]

            st.write(f"### Segment {segment}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Size",
                    f"{len(segment_data):,}",
                    f"{(len(segment_data)/len(df)*100):.1f}%"
                )

            with col2:
                st.metric(
                    "Avg Monthly Charges",
                    f"${segment_data['MonthlyCharges'].mean():.2f}",
                    f"${segment_data['MonthlyCharges'].mean() - df['MonthlyCharges'].mean():.2f}"
                )

            with col3:
                st.metric(
                    "Churn Rate",
                    f"{(segment_data['Churn'].mean()*100):.1f}%",
                    f"{((segment_data['Churn'].mean() - df['Churn'].mean())*100):.1f}%"
                )

            # Contract Type Distribution
            contract_dist = segment_data['ContractType'].value_counts(normalize=True)
            fig = px.pie(
                values=contract_dist.values,
                names=contract_dist.index,
                title=f'Contract Types in Segment {segment}'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Key Characteristics
            st.write("#### Key Characteristics:")

            characteristics = pd.DataFrame({
                'Metric': [
                    'Avg Tenure',
                    'Avg Monthly Charges',
                    'Avg Satisfaction Score',
                    'Most Common Contract',
                    'Most Common Internet Service',
                    'Most Common Payment Method'
                ],
                'Value': [
                    f"{segment_data['Tenure'].mean():.1f} months",
                    f"${segment_data['MonthlyCharges'].mean():.2f}",
                    f"{segment_data['SatisfactionScore'].mean():.2f}",
                    segment_data['ContractType'].mode()[0],
                    segment_data['InternetService'].mode()[0],
                    segment_data['PaymentMethod'].mode()[0]
                ]
            })
            st.table(characteristics)

    # Export Functionality
    if st.button("Export Segmentation Analysis"):
        output = pd.ExcelWriter('segmentation_analysis.xlsx', engine='xlsxwriter')

        # Export segment assignments
        df[['CustomerID', 'Segment'] + selected_features].to_excel(
            output,
            sheet_name='Segment_Assignments',
            index=False
        )

        # Export segment statistics
        segment_stats.to_excel(output, sheet_name='Segment_Statistics')

        # Export segment profiles
        segment_profiles = df.groupby('Segment').agg({
            'Tenure': ['mean', 'min', 'max'],
            'MonthlyCharges': ['mean', 'min', 'max'],
            'SatisfactionScore': ['mean', 'min', 'max'],
            'Churn': 'mean'
        }).round(2)
        segment_profiles.to_excel(output, sheet_name='Segment_Profiles')

        output.save()

        with open('segmentation_analysis.xlsx', 'rb') as f:
            st.download_button(
                label="📥 Download Segmentation Analysis",
                data=f,
                file_name="segmentation_analysis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Recommendations
    st.subheader("📋 Segment-specific Recommendations")

    for segment in range(n_clusters):
        segment_data = df[df['Segment'] == segment]
        churn_rate = segment_data['Churn'].mean()
        avg_charges = segment_data['MonthlyCharges'].mean()
        avg_tenure = segment_data['Tenure'].mean()

        st.write(f"### Segment {segment}")

        if churn_rate > 0.3:
            st.error("High Risk Segment")
            st.write("Recommended Actions:")
            st.write("1. Immediate customer outreach")
            st.write("2. Develop targeted retention offers")
            st.write("3. Service quality review")
        elif churn_rate > 0.15:
            st.warning("Moderate Risk Segment")
            st.write("Recommended Actions:")
            st.write("1. Proactive engagement strategy")
            st.write("2. Loyalty program enrollment")
            st.write("3. Service upgrade opportunities")
        else:
            st.success("Low Risk Segment")
            st.write("Recommended Actions:")
            st.write("1. Maintain service quality")
            st.write("2. Cross-selling opportunities")
            st.write("3. Referral program promotion")
