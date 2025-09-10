import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def render_overview_page(df, visualizer):
    st.subheader("📈 Key Performance Indicators")

    # Top-level filters
    col1, col2 = st.columns(2)
    with col1:
        tenure_range = st.slider(
            "Tenure Range (months)",
            int(df['Tenure'].min()),
            int(df['Tenure'].max()),
            (0, 72)
        )
    with col2:
        contract_types = st.multiselect(
            "Contract Type",
            options=df['ContractType'].unique(),
            default=df['ContractType'].unique()
        )

    # Filter the dataframe
    filtered_df = df[
        (df['Tenure'].between(tenure_range[0], tenure_range[1])) &
        (df['ContractType'].isin(contract_types))
    ]

    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_customers = len(filtered_df)
        st.metric(
            "Total Customers",
            f"{total_customers:,}",
            f"{((total_customers/len(df) - 1) * 100):.1f}% of total"
        )

    with col2:
        churn_rate = (filtered_df['Churn'].mean() * 100)
        st.metric(
            "Churn Rate",
            f"{churn_rate:.1f}%",
            f"{(churn_rate - df['Churn'].mean()*100):.1f}%",
            delta_color="inverse"
        )

    with col3:
        avg_monthly = filtered_df['MonthlyCharges'].mean()
        st.metric(
            "Avg Monthly Charges",
            f"${avg_monthly:.2f}",
            f"${(avg_monthly - df['MonthlyCharges'].mean()):.2f}"
        )

    with col4:
        avg_tenure = filtered_df['Tenure'].mean()
        st.metric(
            "Avg Tenure (months)",
            f"{avg_tenure:.1f}",
            f"{(avg_tenure - df['Tenure'].mean()):.1f}"
        )

    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Customer Demographics", "Service Analysis", "Financial Metrics"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            # Contract Type Distribution
            fig = visualizer.plot_contract_churn()
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Satisfaction Score Distribution
            fig = visualizer.plot_satisfaction_impact()
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            # Service Usage Analysis
            fig = visualizer.plot_service_usage()
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Internet Service Analysis
            internet_churn = pd.crosstab(filtered_df['InternetService'], filtered_df['Churn'])
            fig = px.bar(
                internet_churn,
                title='Internet Service by Churn Status',
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            # Monthly Charges Distribution
            fig = visualizer.plot_monthly_charges_distribution()
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Tenure Analysis
            fig = visualizer.plot_tenure_analysis()
            st.plotly_chart(fig, use_container_width=True)

    # Risk Analysis Section
    st.subheader("🚨 Risk Analysis")

    # Define high-risk customers
    high_risk = filtered_df[
        (filtered_df['MonthlyCharges'] > filtered_df['MonthlyCharges'].quantile(0.75)) &
        (filtered_df['Tenure'] < filtered_df['Tenure'].quantile(0.25)) &
        (filtered_df['ContractType'] == 'Month-to-Month')
    ]

    # Define valuable customers
    valuable_customers = filtered_df[
        (filtered_df['MonthlyCharges'] > filtered_df['MonthlyCharges'].quantile(0.75)) &
        (filtered_df['Tenure'] > filtered_df['Tenure'].quantile(0.75)) &
        (filtered_df['Churn'] == 0)
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.error(f"🔥 {len(high_risk)} High-Risk Customers Identified")
        if len(high_risk) > 0:
            st.write("Characteristics:")
            st.write(f"- Avg Monthly Charges: ${high_risk['MonthlyCharges'].mean():.2f}")
            st.write(f"- Avg Tenure: {high_risk['Tenure'].mean():.1f} months")
            st.write(f"- Churn Rate: {(high_risk['Churn'].mean()*100):.1f}%")

    with col2:
        st.success(f"💎 {len(valuable_customers)} Valuable Customers Identified")
        if len(valuable_customers) > 0:
            st.write("Characteristics:")
            st.write(f"- Avg Monthly Charges: ${valuable_customers['MonthlyCharges'].mean():.2f}")
            st.write(f"- Avg Tenure: {valuable_customers['Tenure'].mean():.1f} months")
            st.write(f"- Total Revenue: ${valuable_customers['TotalCharges'].sum():,.2f}")

    # Export functionality
    if st.button("Export Overview Report"):
        # Use context manager to handle the Excel writer
        with pd.ExcelWriter('customer_overview_report.xlsx', engine='xlsxwriter') as output:
            # Export filtered data
            filtered_df.to_excel(output, sheet_name='Customer Data', index=False)

            # Export summary statistics
            summary_stats = pd.DataFrame({
                'Metric': ['Total Customers', 'Churn Rate', 'Avg Monthly Charges', 'Avg Tenure'],
                'Value': [
                    total_customers,
                    f"{churn_rate:.1f}%",
                    f"${avg_monthly:.2f}",
                    f"{avg_tenure:.1f}"
                ]
            })
            summary_stats.to_excel(output, sheet_name='Summary', index=False)

            # Export risk analysis
            risk_analysis = pd.concat([
                high_risk.assign(Category='High Risk'),
                valuable_customers.assign(Category='Valuable')
            ])
            risk_analysis.to_excel(output, sheet_name='Risk Analysis', index=False)

        # The file is automatically saved when the context manager exits
        with open('customer_overview_report.xlsx', 'rb') as f:
            st.download_button(
                label="📥 Download Report",
                data=f,
                file_name="customer_overview_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
