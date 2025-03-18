# classification.py
import pandas as pd
import numpy as np

def classify_new_users(new_user_data, scaler, pca, centroids_df, training_df):
    """
    Classifies new users by comparing their PCA values to the centroids.
    
    Parameters:
        new_user_data (pd.DataFrame): New user data with the same features as training data.
        scaler (StandardScaler): Fitted scaler from training.
        pca (PCA): Fitted PCA model.
        centroids_df (pd.DataFrame): DataFrame with PCA centroids (columns: 'PC1', 'PC2', 'PC3', 'Cluster').
        training_df (pd.DataFrame): The aggregated training DataFrame (to extract expected feature order).
    
    Returns:
        List: Assigned cluster for each new user.
    """
    # Get the training features (order must match what was used for scaling and PCA)
    training_features = training_df.drop(columns=['id', 'Cluster'], errors='ignore').columns
    # Use the scaler's training means to fill missing columns
    training_means = pd.Series(scaler.mean_, index=training_features)
    new_user_data = new_user_data.reindex(columns=training_features)
    new_user_data = new_user_data.fillna(training_means)
    
    # Standardize and transform using the fitted scaler and PCA
    new_user_scaled = scaler.transform(new_user_data)
    new_user_pca = pca.transform(new_user_scaled)
    
    assigned_clusters = []
    for user in new_user_pca:
        distances = np.linalg.norm(centroids_df[['PC1', 'PC2', 'PC3']].values - user, axis=1)
        assigned_cluster = centroids_df.loc[np.argmin(distances), 'Cluster']
        assigned_clusters.append(assigned_cluster)
    
    return assigned_clusters , new_user_pca