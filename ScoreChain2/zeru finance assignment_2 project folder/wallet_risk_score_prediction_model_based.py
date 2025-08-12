import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Load wallet addresses and simulate features
#wallet_df = pd.read_csv("wallet_risk_scores_rule_based.csv")
wallet_df = pd.read_excel("Wallet_id.xlsx")

# Simulated features for model-based scoring
np.random.seed(42)
wallet_df['tx_count'] = np.random.randint(1, 20, size=len(wallet_df))
wallet_df['total_in'] = np.random.uniform(0.5, 100, size=len(wallet_df))
wallet_df['total_out'] = np.random.uniform(0.5, 100, size=len(wallet_df))
wallet_df['failed_tx'] = np.random.randint(0, 5, size=len(wallet_df))

# Normalize features
features = ['tx_count', 'total_in', 'total_out', 'failed_tx']
X_scaled = MinMaxScaler().fit_transform(wallet_df[features])

# KMeans clustering
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
wallet_df['cluster'] = kmeans.fit_predict(X_scaled)

# Distance to safe cluster
distances = kmeans.transform(X_scaled)
wallet_df['distance_to_safe'] = distances[:, 0]
wallet_df['score_model_based'] = (1 - MinMaxScaler().fit_transform(wallet_df[['distance_to_safe']])) * 1000
wallet_df['score_model_based'] = wallet_df['score_model_based'].astype(int)

# PCA for visualization
pca = PCA(n_components=2)
reduced = pca.fit_transform(X_scaled)
wallet_df['pca1'] = reduced[:, 0]
wallet_df['pca2'] = reduced[:, 1]

# Plot clusters
plt.figure(figsize=(8, 6))
for label in wallet_df['cluster'].unique():
    cluster_data = wallet_df[wallet_df['cluster'] == label]
    plt.scatter(cluster_data['pca1'], cluster_data['pca2'], label=f'Cluster {label}', alpha=0.7)

plt.title("KMeans Clustering of Wallets (PCA 2D View)")
plt.xlabel("PCA 1")
plt.ylabel("PCA 2")
plt.legend()
plt.savefig("kmeans_cluster_visualization.png")

# Save model-based scores
wallet_df[['wallet_id', 'score_model_based']].to_csv("wallet_risk_scores_model_based.csv", index=False)
print("Model-based scoring completed and saved.")