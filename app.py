import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
#

# Set page config
st.set_page_config(
    page_title="ToCs Pathways Explorer",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('outputs/ToCs_Clustered_2025-04-29T13-02_export.xlsx')
    cluster_names = pd.read_csv('outputs/ToCs_PathwaysNames.csv')
    return df, cluster_names

# Main function
def main():
    st.title("ToCs Pathways Explorer")
    
    # Load data
    df, cluster_names = load_data()
    
    # Create a mapping of topic to cluster name and keywords
    cluster_info = dict(zip(
        cluster_names['Topic'],
        zip(cluster_names['Cluster_Name'], cluster_names['Top Keywords'])
    ))
    
    # Sidebar
    st.sidebar.header("Filters")
    
    # Filter by Topic/Cluster with names
    topics = sorted([t for t in df['Topic'].unique() if t != -1])  # Exclude cluster -1
    topic_options = {topic: f"Cluster {topic}: {cluster_info[topic][0] if topic in cluster_info else 'Unnamed'}" 
                    for topic in topics}
    
    selected_topic = st.sidebar.selectbox(
        "Select Cluster/Topic",
        topics,
        format_func=lambda x: topic_options[x]
    )
    
    # Filter by Result Type
    result_types = sorted(df['Result Type'].unique())
    selected_result_type = st.sidebar.multiselect(
        "Filter by Result Type",
        result_types,
        default=result_types[:3]
    )

    # Filter by INIT
    sources = sorted(df['Source_File'].unique())
    selected_sources = st.sidebar.multiselect(
        "Filter by INIT",
        sources,
        default=[],  # No default selection
        help="Select one or more INITs to filter the results"
    )
    
    # Apply filters
    filtered_df = df[
        (df['Topic'] == selected_topic) &
        (df['Result Type'].isin(selected_result_type))
    ]

    # Apply source filter if any sources are selected
    if selected_sources:
        filtered_df = filtered_df[filtered_df['Source_File'].isin(selected_sources)]
    
    # Main content area - using columns for layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display cluster name and keywords
        if selected_topic in cluster_info:
            cluster_name, keywords = cluster_info[selected_topic]
            st.header(f"Cluster {selected_topic}: {cluster_name}")
            st.markdown(f"**Top Keywords:** {keywords}")
        else:
            st.header(f"Cluster {selected_topic}")
        
        # Cluster Statistics
        st.subheader("Cluster Statistics")
        stats_cols = st.columns(4)
        
        with stats_cols[0]:
            st.metric("Total Entries", len(filtered_df))
        with stats_cols[1]:
            st.metric("Total INITs", filtered_df['Source_File'].nunique())
        with stats_cols[2]:
            st.metric("Result Types", filtered_df['Result Type'].nunique())
        with stats_cols[3]:
            st.metric("Work Packages", filtered_df['WP Title'].nunique())
        
        # Result Statements Table
        st.subheader("Result Statements")
        st.dataframe(
            filtered_df[[
                'Result Statement', 
                'Result type (outcome or output)',
                'Result Type', 
                'Indicator',
                'Type',
                'Unit of measurement',
                'WP Title', 
                'Source_File'
            ]],
            hide_index=True,
            column_config={
                "Result Statement": st.column_config.TextColumn("Result Statement", width="large"),
                "Result type (outcome or output)": st.column_config.TextColumn("Outcome/Output", width="medium"),
                "Result Type": st.column_config.TextColumn("Type", width="medium"),
                "Indicator": st.column_config.TextColumn("Indicator", width="medium"),
                "Type": st.column_config.TextColumn("Indicator Type", width="medium"),
                "Unit of measurement": st.column_config.TextColumn("Unit", width="medium"),
                "WP Title": st.column_config.TextColumn("Work Package", width="medium"),
                "Source_File": st.column_config.TextColumn("INIT", width="medium")
            }
        )
    
    with col2:
        # Help section
        st.info("""
        **How to use this dashboard:**
        
        1. Use the sidebar to select a specific cluster
        2. Filter by Result Types if needed
        3. Filter by INITs if needed
        4. Explore the detailed results in the table
        5. Scroll down to see overall statistics
        """)
    
    # Clusters Overview Section
    st.header("Clusters Overview")
    
    # Get cluster sizes (excluding -1)
    cluster_sizes = df[df['Topic'] != -1]['Topic'].value_counts().sort_index()
    
    # Create overview data
    overview_data = []
    for topic in cluster_sizes.index:
        if topic in cluster_info:
            cluster_name, keywords = cluster_info[topic]
            overview_data.append({
                'Cluster Number': f"Cluster {topic}",
                'Name': cluster_name,
                'Size': cluster_sizes[topic],
                'Keywords': keywords
            })
    
    # Convert to DataFrame and display as table
    overview_df = pd.DataFrame(overview_data)
    
    # Display the overview table with custom formatting
    st.dataframe(
        overview_df,
        hide_index=True,
        column_config={
            "Cluster Number": st.column_config.TextColumn("Cluster", width="small"),
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Size": st.column_config.NumberColumn("Size", width="small"),
            "Keywords": st.column_config.TextColumn("Top Keywords", width="large")
        }
    )
    
    # Additional Insights
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Result Types Across All Clusters")
        result_types_all = df[df['Topic'] != -1]['Result Type'].value_counts()  # Exclude cluster -1
        fig_all_types = px.pie(
            values=result_types_all.values,
            names=result_types_all.index,
            title="Overall Distribution of Result Types"
        )
        st.plotly_chart(fig_all_types, use_container_width=True)
    
    with col4:
        st.subheader("Top Work Packages")
        wp_counts = df[df['Topic'] != -1]['WP Title'].value_counts().head(10)  # Exclude cluster -1
        fig_wp = px.bar(
            x=wp_counts.values,
            y=wp_counts.index,
            orientation='h',
            title="Top 10 Work Packages"
        )
        fig_wp.update_layout(
            xaxis_title="Count",
            yaxis_title="Work Package",
            height=400
        )
        st.plotly_chart(fig_wp, use_container_width=True)

if __name__ == "__main__":
    main()
