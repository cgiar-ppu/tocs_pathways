import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="ToCs Pathways Explorer",
    layout="wide"
)

# Use session state to maintain selected tab
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 0

# Load data with cache bypass
def load_data():
    # Add timestamp to force reload when needed
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    try:
        df = pd.read_excel('outputs/ToCs_Clustered_with_Topics.xlsx')
        
        # Handle NaN and type conversions immediately
        df['Cluster_Name'] = df['Cluster_Name'].fillna("Uncategorized")
        df['Topic'] = df['Topic'].fillna(-1).astype(int)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def main():
    st.title("ToCs Pathways Explorer")
    
    try:
        # Load data
        df = load_data()
        if df is None:
            st.error("Failed to load data. Please check the data files.")
            return
        
        # Add download button for raw data
        st.download_button(
            label="Download Full Dataset",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="ToCs_Pathways_Data.csv",
            mime="text/csv",
            help="Download the complete dataset as a CSV file"
        )
        
        # Calculate totals
        total_indicators = df[
            (df['Topic'] != -1) & 
            (df['Indicator'].notna())
        ]['Indicator'].nunique()
        
        total_indicator_topics = df['Cluster_Name'].nunique()
        
        # Sidebar
        st.sidebar.header("Filters")
        
        # Show total number of indicators
        total_unique_indicators = df['Indicator'].nunique()
        total_topics = df['Cluster_Name'].nunique()
        
        # Create metrics for the overview
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric("Total Unique Indicators", total_unique_indicators)
        with metric_cols[1]:
            st.metric("Total Topics", total_topics)
        with metric_cols[2]:
            avg_indicators_per_topic = round(total_unique_indicators / total_topics, 1)
            st.metric("Average Indicators per Topic", avg_indicators_per_topic)
        
        # Filter by Indicator Topic
        indicator_topics = ["ALL"] + sorted([str(topic) for topic in df['Cluster_Name'].unique() if pd.notna(topic)])
        selected_indicator_topic = st.selectbox(
            "Select Indicator Topic",
            indicator_topics,
            index=0  # Set default to "ALL"
        )
        
        # Apply filters for Indicator Topic view
        if selected_indicator_topic == "ALL":
            filtered_df_it = df
        else:
            filtered_df_it = df[df['Cluster_Name'] == selected_indicator_topic]
        
        # Indicator topic statistics
        st.subheader("Topic Statistics")
        it_stats_cols = st.columns(4)
        
        with it_stats_cols[0]:
            st.metric("Total Indicators", filtered_df_it['Indicator'].nunique())
        with it_stats_cols[1]:
            st.metric("Total INITs", filtered_df_it['Source_File'].nunique())
        with it_stats_cols[2]:
            st.metric("Result Types", filtered_df_it['Result Type'].nunique())
        with it_stats_cols[3]:
            st.metric("Work Packages", filtered_df_it['WP Title'].nunique())
        
        # Show Indicators and their context
        st.subheader("Indicators in Topic")
        display_cols = [
            'Indicator',
            'Result Statement',
            'Result Type',
            'WP Title',
            'Source_File',
            'Cluster_Name'  # Added to show topic when ALL is selected
        ]
        display_cols = [col for col in display_cols if col in filtered_df_it.columns]
        st.dataframe(filtered_df_it[display_cols].drop_duplicates(), hide_index=True)
        
        # Sidebar filters
        st.sidebar.subheader("Global Filters")
        
        # Filter by Result Type
        result_types = sorted(df['Result Type'].dropna().unique())
        selected_result_type = st.sidebar.multiselect(
            "Filter by Result Type",
            result_types,
            default=result_types[:3]
        )

        # Filter by INIT
        sources = sorted(df['Source_File'].dropna().unique())
        selected_sources = st.sidebar.multiselect(
            "Filter by INIT",
            sources,
            default=[],
            help="Select one or more INITs to filter the results"
        )

        # Filter by Indicator
        indicators = sorted(df['Indicator'].dropna().unique())
        selected_indicators = st.sidebar.multiselect(
            "Filter by Indicator",
            indicators,
            default=[],
            help="Select one or more indicators to filter the results"
        )
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please check the data format and try again.")

if __name__ == "__main__":
    main()
