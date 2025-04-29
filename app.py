import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="ToCs Pathways Explorer",
    page_title_align="center",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('outputs/ToCs_Clustered_2025-04-29T13-02_export.xlsx')
    return df

# Main function
def main():
    st.title("ToCs Pathways Explorer")
    
    # Load data
    df = load_data()
    
    # Sidebar
    st.sidebar.header("Filters")
    
    # Filter by Topic/Cluster
    topics = sorted(df['Topic'].unique())
    selected_topic = st.sidebar.selectbox(
        "Select Cluster/Topic",
        topics,
        format_func=lambda x: f"Cluster {x}"
    )
    
    # Filter by Result Type
    result_types = sorted(df['Result Type'].unique())
    selected_result_type = st.sidebar.multiselect(
        "Filter by Result Type",
        result_types,
        default=result_types[:3]
    )
    
    # Apply filters
    filtered_df = df[
        (df['Topic'] == selected_topic) &
        (df['Result Type'].isin(selected_result_type))
    ]
    
    # Main content area - using columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"Cluster {selected_topic} Analysis")
        
        # Cluster Statistics
        st.subheader("Cluster Statistics")
        stats_cols = st.columns(4)
        
        with stats_cols[0]:
            st.metric("Total Entries", len(filtered_df))
        with stats_cols[1]:
            st.metric("Unique Sources", filtered_df['Source_File'].nunique())
        with stats_cols[2]:
            st.metric("Result Types", filtered_df['Result Type'].nunique())
        with stats_cols[3]:
            st.metric("Work Packages", filtered_df['WP Title'].nunique())
        
        # Result Statements Table
        st.subheader("Result Statements")
        st.dataframe(
            filtered_df[['Result Statement', 'Result Type', 'WP Title', 'Source_File']],
            hide_index=True,
            column_config={
                "Result Statement": st.column_config.TextColumn("Result Statement", width="large"),
                "Result Type": st.column_config.TextColumn("Type", width="medium"),
                "WP Title": st.column_config.TextColumn("Work Package", width="medium"),
                "Source_File": st.column_config.TextColumn("Source", width="medium")
            }
        )
    
    with col2:
        # Distribution of Result Types
        st.subheader("Result Types Distribution")
        result_type_counts = filtered_df['Result Type'].value_counts()
        fig_types = px.pie(
            values=result_type_counts.values,
            names=result_type_counts.index,
            title="Distribution of Result Types"
        )
        st.plotly_chart(fig_types, use_container_width=True)
        
        # Source Files Distribution
        st.subheader("Source Files Distribution")
        source_counts = filtered_df['Source_File'].value_counts()
        fig_sources = px.bar(
            x=source_counts.values,
            y=source_counts.index,
            orientation='h',
            title="Number of Entries by Source"
        )
        fig_sources.update_layout(
            xaxis_title="Count",
            yaxis_title="Source File",
            height=400
        )
        st.plotly_chart(fig_sources, use_container_width=True)
    
    # Cluster Overview Section
    st.header("Clusters Overview")
    
    # Cluster sizes
    cluster_sizes = df['Topic'].value_counts().sort_index()
    fig_clusters = px.bar(
        x=cluster_sizes.index,
        y=cluster_sizes.values,
        title="Size of Each Cluster",
        labels={'x': 'Cluster', 'y': 'Number of Entries'}
    )
    fig_clusters.update_layout(height=400)
    st.plotly_chart(fig_clusters, use_container_width=True)
    
    # Additional Insights
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Result Types Across All Clusters")
        result_types_all = df['Result Type'].value_counts()
        fig_all_types = px.pie(
            values=result_types_all.values,
            names=result_types_all.index,
            title="Overall Distribution of Result Types"
        )
        st.plotly_chart(fig_all_types, use_container_width=True)
    
    with col4:
        st.subheader("Top Work Packages")
        wp_counts = df['WP Title'].value_counts().head(10)
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
