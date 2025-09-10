import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render_detailed_analysis_page(df, visualizer):
    st.subheader("🔍 Detailed Customer Analysis")

    # Advanced Filtering
    with st.expander("Advanced Filters", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            contract_filter = st.multiselect(
                "Contract Type",
                options=df['ContractType'].unique(),
                default=df['ContractType'].unique()
            )

            monthly_charges_range = st.slider(
                "Monthly Charges ($)",
                float(df['MonthlyCharges'].min()),
                float(df['MonthlyCharges'].max()),
                (float(df['MonthlyCharges'].min()), float(df['MonthlyCharges'].max()))
            )

        with col2:
            internet_filter = st.multiselect(
                "Internet Service",
                options=df['InternetService'].unique(),
                default=df['InternetService'].unique()
            )

            tenure_range = st.slider(
                "Tenure (months)",
                int(df['Tenure'].min()),
                int(df['Tenure'].max()),
                (int(df['Tenure'].min()), int(df['Tenure'].max()))
            )

        with col3:
            payment_filter = st.multiselect(
                "Payment Method",
                options=df['PaymentMethod'].unique(),
                default=df['PaymentMethod'].unique()
            )

            satisfaction_range = st.slider(
                "Satisfaction Score",
                float(df['SatisfactionScore'].min()),
                float(df['SatisfactionScore'].max()),
                (float(df['SatisfactionScore'].min()), float(df['SatisfactionScore'].max()))
            )

    # Apply filters
    filtered_df = df[
        (df['ContractType'].isin(contract_filter)) &
        (df['InternetService'].isin(internet_filter)) &
        (df['PaymentMethod'].isin(payment_filter)) &
        (df['MonthlyCharges'].between(monthly_charges_range[0], monthly_charges_range[1])) &
        (df['Tenure'].between(tenure_range[0], tenure_range[1])) &
        (df['SatisfactionScore'].between(satisfaction_range[0], satisfaction_range[1]))
    ]

    # Show filtered data statistics
    st.write(f"Filtered Data Points: {len(filtered_df)} ({(len(filtered_df)/len(df)*100):.1f}% of total)")

    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "Revenue Analysis",
        "Customer Behavior",
        "Service Analysis",
        "Churn Patterns"
    ])

    with tab1:
        st.subheader("Revenue Analysis")
        col1, col2 = st.columns(2)

        with col1:
            # Monthly Revenue Trend
            monthly_revenue = filtered_df.groupby('Tenure')['MonthlyCharges'].sum().reset_index()
            fig = px.line(
                monthly_revenue,
                x='Tenure',
                y='MonthlyCharges',
                title='Monthly Revenue by Tenure'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Revenue by Contract Type
            contract_revenue = filtered_df.groupby('ContractType').agg({
                'MonthlyCharges': ['sum', 'mean'],
                'CustomerID': 'count'  # Using CustomerID for count
            }).reset_index()

            contract_revenue.columns = ['ContractType', 'Total_Revenue', 'Avg_Revenue', 'Customer_Count']
            fig = px.bar(
                contract_revenue,
                x='ContractType',
                y='Total_Revenue',
                title='Total Revenue by Contract Type',
                color='Avg_Revenue',
                text=contract_revenue['Customer_Count'].apply(lambda x: f'n={x}')
            )
            fig.update_traces(textposition='outside')

            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Customer Behavior Analysis")
        col1, col2 = st.columns(2)

        with col1:
            # Satisfaction vs Charges
            fig = px.scatter(
                filtered_df,
                x='MonthlyCharges',
                y='SatisfactionScore',
                color='Churn',
                size='Tenure',
                title='Satisfaction vs Monthly Charges',
                trendline="ols"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Payment Method Analysis
            payment_churn = pd.crosstab(
                filtered_df['PaymentMethod'],
                filtered_df['Churn'],
                values=filtered_df['MonthlyCharges'],
                aggfunc='mean'
            )
            fig = px.bar(
                payment_churn,
                title='Average Monthly Charges by Payment Method and Churn Status',
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Service Analysis")
        col1, col2 = st.columns(2)

        with col1:
            # Service Combinations
            service_cols = ['PhoneService', 'InternetService', 'StreamingTV', 'StreamingMovies']
            service_combinations = filtered_df[service_cols].value_counts().reset_index()
            service_combinations.columns = [*service_cols, 'count']

            fig = px.treemap(
                service_combinations,
                path=service_cols,
                values='count',
                title='Service Combination Analysis'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Service Impact on Churn
            service_impact = []
            for service in service_cols:
                churn_rate = filtered_df.groupby(service)['Churn'].mean()
                service_impact.append({
                    'Service': service,
                    'Feature': churn_rate.index,
                    'Churn_Rate': churn_rate.values
                })

            # Create a DataFrame from the collected data
            service_impact_df = pd.concat([
                pd.DataFrame(item['Churn_Rate'],
                            columns=['Churn_Rate'],
                            index=item['Feature']).assign(Service=item['Service'])
                for item in service_impact
            ]).reset_index()

            fig = px.bar(
                service_impact_df,
                x='Service',
                y='Churn_Rate',
                color='index',
                title='Service Impact on Churn Rate',
                labels={'index': 'Feature Value', 'Churn_Rate': 'Churn Rate'}
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Churn Pattern Analysis")
        col1, col2 = st.columns(2)

        with col1:
            # Churn Rate by Tenure and Contract
            # Create tenure bins and convert to string labels
            tenure_bins = pd.qcut(filtered_df['Tenure'], 4)
            filtered_df['TenureBin'] = tenure_bins.apply(lambda x: f'{int(x.left)}-{int(x.right)} months')

            churn_heat = pd.pivot_table(
                filtered_df,
                values='Churn',
                index='ContractType',
                columns='TenureBin',
                aggfunc='mean'
            )

            fig = px.imshow(
                churn_heat,
                title='Churn Rate by Tenure and Contract Type',
                color_continuous_scale='RdYlGn_r',
                labels={'color': 'Churn Rate'}
            )
            # Improve readability of the heatmap
            fig.update_layout(
                xaxis_title="Tenure Range",
                yaxis_title="Contract Type"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Churn Factors Correlation
            numeric_cols = ['Tenure', 'MonthlyCharges', 'TotalCharges', 'SatisfactionScore']
            corr_matrix = filtered_df[numeric_cols + ['Churn']].corr()['Churn'].sort_values()

            fig = px.bar(
                y=corr_matrix.index,
                x=corr_matrix.values,
                title='Correlation with Churn',
                orientation='h',
                labels={'x': 'Correlation Coefficient', 'y': 'Features'}
            )
            st.plotly_chart(fig, use_container_width=True)

    # Customer Lifetime Value Analysis
    st.subheader("📈 Customer Lifetime Value (CLV) Analysis")

    # Calculate CLV
    filtered_df['CLV'] = filtered_df['MonthlyCharges'] * filtered_df['Tenure']

    col1, col2 = st.columns(2)

    with col1:
        # CLV Distribution
        fig = px.histogram(
            filtered_df,
            x='CLV',
            color='Churn',
            marginal='box',
            title='Customer Lifetime Value Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # CLV by Contract Type
        fig = px.box(
            filtered_df,
            x='ContractType',
            y='CLV',
            color='Churn',
            title='CLV by Contract Type'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Export functionality
    if st.button("Export Detailed Analysis"):
        # Use context manager for ExcelWriter
        with pd.ExcelWriter('detailed_analysis_report.xlsx', engine='xlsxwriter') as output:
            # Export filtered data
            filtered_df.to_excel(output, sheet_name='Filtered Data', index=False)

            # Export summary statistics
            summary_stats = filtered_df.describe()
            summary_stats.to_excel(output, sheet_name='Summary Statistics')

            # Export correlation matrix
            corr_matrix.to_excel(output, sheet_name='Correlations')

        # File is automatically saved when context manager exits
        with open('detailed_analysis_report.xlsx', 'rb') as f:
            st.download_button(
                label="📥 Download Detailed Analysis",
                data=f,
                file_name="detailed_analysis_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
