import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from collections import defaultdict


def main():
    # Load the data
    df = pd.read_csv('outputs/SNAP_onlyOutcomes_2025-04-30T04-06_export.csv')
    
    # Load the pathway names
    pathway_names = pd.read_csv('outputs/ToCs_PathwaysNames.csv')
    
    # Merge the pathway names with our dataframe based on the Topic column
    df = df.merge(pathway_names[['Topic', 'Cluster_Name']], 
                 on='Topic',
                 how='left')
    
    # Save processed data
    df.to_excel('outputs/ToCs_Clustered_with_Topics.xlsx', index=False)
    
    # Print statistics
    print(f"Number of rows: {len(df)}")
    print(f"Number of unique cluster names: {len(df['Cluster_Name'].unique())}")
    
    # Print cluster distribution
    cluster_counts = df['Cluster_Name'].value_counts()
    print("\nTop 10 largest clusters:")
    print(cluster_counts.head(10))

if __name__ == "__main__":
    main() 