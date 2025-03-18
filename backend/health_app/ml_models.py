# ml_models.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import linkage, fcluster

def aggregate_data(df):
    agg_dict = {
        'calories': 'mean',
        'distance': 'mean',
        'steps': 'mean',
        'lightly_active_minutes': 'mean',
        'moderately_active_minutes': 'mean',
        'very_active_minutes': 'mean',
        'sedentary_minutes': 'mean',
        'sleep_duration': 'mean',
        'minutesAsleep': 'mean',
        'bpm': 'mean',
        'resting_hr': 'mean',
        'filteredDemographicVO2Max': 'mean',
        'nightly_temperature': 'mean',
        'age': 'first',
        'gender': 'first',
        'bmi': 'first'
    }
    agg_dict = {col: func for col, func in agg_dict.items() if col in df.columns}
    df_agg = df.groupby('id').agg(agg_dict).reset_index()
    return df_agg

def preprocess_data(df):
    num_cols = df.select_dtypes(include=['number']).columns
    df[num_cols] = df[num_cols].apply(lambda x: x.fillna(x.median()))
    encoder = LabelEncoder()
    for col in ['age', 'gender', 'bmi']:
        if col in df.columns:
            df[col] = encoder.fit_transform(df[col])
    return df

def standardize_data(df):
    scaler = StandardScaler()
    features = df.drop(columns=['id'])
    df_scaled = scaler.fit_transform(features)
    return df_scaled, scaler

def hierarchical_clustering(df_scaled, df_original, n_clusters=5):
    linkage_matrix = linkage(df_scaled, method='ward')
    df_original['Cluster'] = fcluster(linkage_matrix, n_clusters, criterion='maxclust')
    return df_original, linkage_matrix


def build_pca_model(df_aggregated, scaler):
    """
    Fits a PCA (with 3 components) on the standardized features from df_aggregated
    and computes centroids in the PCA space for each cluster.
    """

    df_features = df_aggregated.drop(columns=['id', 'Cluster'], errors='ignore')
    
    # Standardize data
    df_scaled = scaler.fit_transform(df_features)
    
    # Fit PCA
    pca = PCA(n_components=3, random_state=42)
    pca_result = pca.fit_transform(df_scaled)

    # Compute centroids in scaled space before PCA transformation
    clusters = sorted(df_aggregated['Cluster'].unique())
    cluster_centroids = []
    for cluster in clusters:
        cluster_data = df_scaled[df_aggregated['Cluster'] == cluster]
        if len(cluster_data) > 0:
            centroid = cluster_data.mean(axis=0)
            cluster_centroids.append(centroid)

    # Transform centroids to PCA space
    pca_centroids = pca.transform(np.array(cluster_centroids))
    
    # Convert to DataFrame
    centroids_df = pd.DataFrame(pca_centroids, columns=['PC1', 'PC2', 'PC3'])
    centroids_df['Cluster'] = clusters

    # **Apply the conditional flipping rule**
    if centroids_df.loc[centroids_df['Cluster'] == 1, 'PC1'].values[0] > 0:
        print("DEBUG: PC1 of cluster 1 is positive, flipping signs...")
        centroids_df[['PC1', 'PC2', 'PC3']] *= -1  # Flip all PCA scores

    # Print Debug Information
    print("DEBUG: Centroids after PCA transformation (sign-corrected):")
    print(centroids_df)

    return pca, centroids_df

# ===== Execution Pipeline =====

# Load your dataset
import os

# Récupérer le répertoire du script en cours d'exécution
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construire le chemin relatif vers le fichier CSV
csv_path = os.path.join(script_dir, "df_daily2.csv")

# Charger le fichier
df_daily_cleaned = pd.read_csv(csv_path)

# Process the data
df_aggregated = aggregate_data(df_daily_cleaned)
df_aggregated = preprocess_data(df_aggregated)
df_scaled, scaler = standardize_data(df_aggregated)
df_aggregated, linkage_matrix = hierarchical_clustering(df_scaled, df_aggregated)

# Build PCA model and obtain centroids (no plotting, no printouts)
pca, centroids_df = build_pca_model(df_aggregated, scaler)

# Debug: print centroids immediately after calculation
print("\n=== Centroids from ml_models.py ===")
print(centroids_df)
print("===================================\n")

# Expose these objects for other modules
_all_ = ['df_aggregated', 'scaler', 'pca','centroids_df']