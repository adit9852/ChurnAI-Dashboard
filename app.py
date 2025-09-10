import streamlit as st
import logging
from src.config import config
from src.data_loader import DataLoader
from src.data_processor import DataProcessor
from src.visualization import Visualizer
from src.pages import (
    overview,
    detailed_analysis,
    prediction,
    segmentation,
    advanced_analytics
)

# Setup logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load CSS
def load_css():
    with open(config.style_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    load_css()

    st.markdown("<h1 class='title'>Customer Churn Analysis Dashboard</h1>",
                unsafe_allow_html=True)

    # Load data
    df = DataLoader.load_data()
    if df is None:
        st.stop()

    # Initialize components
    data_processor = DataProcessor(df)
    visualizer = Visualizer(df)

    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Overview Dashboard", "Detailed Analysis", "Prediction System",
            "Customer Segments", "Advanced Analytics"]  # Add the new page
    )

    if page == "Overview Dashboard":
        overview.render_overview_page(df, visualizer)
    elif page == "Detailed Analysis":
        detailed_analysis.render_detailed_analysis_page(df, visualizer)
    elif page == "Prediction System":
        prediction.render_prediction_page(df, data_processor)
    elif page == "Customer Segments":
        segmentation.render_segmentation_page(df, data_processor, visualizer)
    elif page == "Advanced Analytics":
        advanced_analytics.render_advanced_analytics_page(df)

if __name__ == "__main__":
    main()
