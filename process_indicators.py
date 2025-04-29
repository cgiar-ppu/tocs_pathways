import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from collections import defaultdict
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import hdbscan

def preprocess_text(text):
    if pd.isna(text):
        return ""
    # Convert to lowercase
    text = str(text).lower()
    # Remove special characters and extra spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def cluster_indicators(indicators, similarity_threshold=0.6):
    # Preprocess indicators
    processed_indicators = [preprocess_text(ind) for ind in indicators]
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(min_df=1, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(processed_indicators)
    
    # Calculate similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Create clusters
    clusters = defaultdict(list)
    used_indices = set()
    cluster_id = 0
    
    # For each indicator
    for i in range(len(indicators)):
        if i in used_indices:
            continue
            
        # Find similar indicators
        similar_indices = np.where(similarity_matrix[i] >= similarity_threshold)[0]
        
        # If we found similar indicators
        if len(similar_indices) > 0:
            # Add all similar indicators to the cluster
            cluster = []
            for idx in similar_indices:
                if idx not in used_indices:
                    cluster.append(indicators[idx])
                    used_indices.add(idx)
            
            # Sort cluster by length and use the shortest as representative
            cluster.sort(key=len)
            clusters[cluster[0]] = cluster
            cluster_id += 1
    
    # Create mapping from original indicator to cluster representative
    indicator_to_cluster = {}
    for representative, cluster_members in clusters.items():
        for member in cluster_members:
            indicator_to_cluster[member] = representative
    
    return indicator_to_cluster

def perform_bertopic_clustering(indicators):
    # Initialize the sentence transformer model
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Initialize HDBSCAN
    hdbscan_model = hdbscan.HDBSCAN(min_cluster_size=5, 
                                   min_samples=2,
                                   metric='euclidean',
                                   cluster_selection_method='eom')
    
    # Initialize BERTopic
    topic_model = BERTopic(
        embedding_model=embedding_model,
        hdbscan_model=hdbscan_model,
        verbose=True
    )
    
    # Fit the model and get topics
    topics, probs = topic_model.fit_transform(indicators)
    
    # Get topic info
    topic_info = topic_model.get_topic_info()
    
    # Create a mapping of topic numbers to representative documents
    topic_to_name = {}
    for topic in topic_info['Topic'].unique():
        if topic != -1:  # Skip outlier topic
            # Get the topic's words and their scores
            topic_words = topic_model.get_topic(topic)
            if topic_words:
                # Find the document that best represents this topic
                topic_docs = [doc for doc in indicators if any(word[0] in doc.lower() for word in topic_words[:3])]
                if topic_docs:
                    # Use the shortest document as the topic name
                    topic_to_name[topic] = min(topic_docs, key=len)
    
    # Create mapping from topic number to topic name
    topic_mapping = {idx: (topic_to_name.get(idx, "Outlier") if idx != -1 else "Outlier")
                    for idx in topics}
    
    return topics, topic_mapping

def main():
    # Load the data
    df = pd.read_excel('outputs/ToCs_Clustered_2025-04-29T13-02_export.xlsx')
    
    # Get unique indicators (excluding NaN)
    unique_indicators = df['Indicator'].dropna().unique()
    
    # Perform traditional clustering
    indicator_clusters = cluster_indicators(unique_indicators)
    
    # Perform BERTopic clustering
    print("\nPerforming BERTopic clustering...")
    topics, topic_mapping = perform_bertopic_clustering(unique_indicators)
    
    # Create mapping from indicator to topic name
    indicator_to_topic = {ind: topic_mapping[top] for ind, top in zip(unique_indicators, topics)}
    
    # Save the traditional clustering mapping
    mapping_df = pd.DataFrame({
        'Original_Indicator': list(indicator_clusters.keys()),
        'Clustered_Indicator': list(indicator_clusters.values())
    })
    mapping_df.to_csv('outputs/indicator_clusters.csv', index=False)
    
    # Add both clustered columns to original data
    df['Clustered_Indicator'] = df['Indicator'].map(indicator_clusters)
    df['Topic_Name'] = df['Indicator'].map(indicator_to_topic)
    
    # Save processed data
    df.to_excel('outputs/ToCs_Clustered_with_Topics.xlsx', index=False)
    
    # Print statistics
    print(f"Original unique indicators: {len(unique_indicators)}")
    print(f"Clustered unique indicators: {len(set(indicator_clusters.values()))}")
    print(f"BERTopic unique topics: {len(set(topic_mapping.values()))}")
    
    # Print topic distribution
    topic_counts = df['Topic_Name'].value_counts()
    print("\nTop 10 largest topics:")
    print(topic_counts.head(10))

if __name__ == "__main__":
    main() 