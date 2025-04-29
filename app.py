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
        cluster_names = pd.read_csv('outputs/ToCs_PathwaysNames.csv')
        
        # Handle NaN and type conversions immediately
        df['Topic_Name'] = df['Topic_Name'].fillna("Uncategorized")
        df['Topic'] = df['Topic'].fillna(-1).astype(int)
        
        return df, cluster_names
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def main():
    st.title("ToCs Pathways Explorer")
    
    try:
        # Load data
        df, cluster_names = load_data()
        if df is None or cluster_names is None:
            st.error("Failed to load data. Please check the data files.")
            return
        
        # Create a mapping of topic to cluster name and keywords
        cluster_info = dict(zip(
            cluster_names['Topic'],
            zip(cluster_names['Cluster_Name'], cluster_names['Top Keywords'])
        ))
        
        # Calculate totals
        total_indicators = df[
            (df['Topic'] != -1) & 
            (df['Indicator'].notna())
        ]['Indicator'].nunique()
        
        total_indicator_topics = df['Topic_Name'].nunique()
        
        # Sidebar
        st.sidebar.header("Filters")
        
        # Add tabs for different views with session state
        tabs = ["Results Statement Clusters", "Indicator Topics"]
        current_tab = st.radio("Select View", tabs, index=st.session_state.current_tab, horizontal=True)
        st.session_state.current_tab = tabs.index(current_tab)
        
        if current_tab == "Results Statement Clusters":
            # Filter by Topic/Cluster with names
            topics = sorted([t for t in df['Topic'].unique() if t != -1])  # Exclude cluster -1
            topic_options = {int(topic): f"Cluster {topic}: {cluster_info[topic][0] if topic in cluster_info else 'Unnamed'}" 
                           for topic in topics}
            
            selected_topic = st.selectbox(
                "Select Results Statement Cluster",
                topics,
                format_func=lambda x: topic_options[int(x)]
            )
            
            # Apply filters for Results Statement view
            filtered_df_rs = df[df['Topic'] == selected_topic]
            
            # Display cluster info
            if selected_topic in cluster_info:
                cluster_name, keywords = cluster_info[selected_topic]
                st.header(f"Cluster {selected_topic}: {cluster_name}")
                st.markdown(f"**Top Keywords:** {keywords}")
            else:
                st.header(f"Cluster {selected_topic}")
            
            # Results Statement cluster statistics
            st.subheader("Cluster Statistics")
            rs_stats_cols = st.columns(4)
            
            with rs_stats_cols[0]:
                st.metric("Total Entries", len(filtered_df_rs))
            with rs_stats_cols[1]:
                st.metric("Total INITs", filtered_df_rs['Source_File'].nunique())
            with rs_stats_cols[2]:
                st.metric("Result Types", filtered_df_rs['Result Type'].nunique())
            with rs_stats_cols[3]:
                st.metric("Work Packages", filtered_df_rs['WP Title'].nunique())
            
            # Show Results Statements
            st.subheader("Result Statements")
            display_cols = [
                'Result Statement', 
                'Result type (outcome or output)',
                'Result Type', 
                'Indicator',
                'Topic_Name',
                'WP Title', 
                'Source_File'
            ]
            display_cols = [col for col in display_cols if col in filtered_df_rs.columns]
            st.dataframe(filtered_df_rs[display_cols], hide_index=True)
            
        else:  # Indicator Topics tab
            # Show total number of indicators
            total_unique_indicators = df['Indicator'].nunique()
            total_topics = df['Topic_Name'].nunique()
            
            # Create two columns for the metrics
            metric_cols = st.columns(3)
            with metric_cols[0]:
                st.metric("Total Unique Indicators", total_unique_indicators)
            with metric_cols[1]:
                st.metric("Total Topics", total_topics)
            with metric_cols[2]:
                avg_indicators_per_topic = round(total_unique_indicators / total_topics, 1)
                st.metric("Average Indicators per Topic", avg_indicators_per_topic)
            
            # Filter by Indicator Topic
            indicator_topics = sorted([str(topic) for topic in df['Topic_Name'].unique() if pd.notna(topic)])
            selected_indicator_topic = st.selectbox(
                "Select Indicator Topic",
                indicator_topics
            )
            
            # Apply filters for Indicator Topic view
            filtered_df_it = df[df['Topic_Name'] == selected_indicator_topic]
            
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
                'Source_File'
            ]
            display_cols = [col for col in display_cols if col in filtered_df_it.columns]
            st.dataframe(filtered_df_it[display_cols].drop_duplicates(), hide_index=True)
        
        # Sidebar filters (apply to both views)
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
        
        # Overall Statistics Section
        st.header("Overall Statistics")
        
        # Create three columns for different visualizations
        viz_col1, viz_col2, viz_col3 = st.columns(3)
        
        with viz_col1:
            # Results Statement Clusters Overview
            rs_cluster_sizes = df[df['Topic'] != -1]['Topic'].value_counts()
            fig_rs_clusters = px.bar(
                x=rs_cluster_sizes.values[:10],
                y=[topic_options[idx] for idx in rs_cluster_sizes.index[:10]],
                orientation='h',
                title="Top 10 Results Statement Clusters"
            )
            fig_rs_clusters.update_layout(height=400)
            st.plotly_chart(fig_rs_clusters, use_container_width=True)
        
        with viz_col2:
            # Indicator Topics Overview
            indicator_topic_sizes = df['Topic_Name'].value_counts()
            fig_indicator_topics = px.bar(
                x=indicator_topic_sizes.values[:10],
                y=indicator_topic_sizes.index[:10],
                orientation='h',
                title="Top 10 Indicator Topics"
            )
            fig_indicator_topics.update_layout(height=400)
            st.plotly_chart(fig_indicator_topics, use_container_width=True)
        
        with viz_col3:
            # Result Types Distribution
            result_type_dist = df['Result Type'].value_counts()
            fig_result_types = px.pie(
                values=result_type_dist.values,
                names=result_type_dist.index,
                title="Distribution of Result Types"
            )
            fig_result_types.update_layout(height=400)
            st.plotly_chart(fig_result_types, use_container_width=True)
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please check the data format and try again.")

if __name__ == "__main__":
    main()
