import pandas as pd
import numpy as np
import requests
import time
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

ETHERSCAN_API_KEY = "YOUR_ETHERSCAN_API_KEY"  # Replace with your actual API key

def fetch_transactions(wallet_address):
    base_url = "https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet_address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": ETHERSCAN_API_KEY
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if data["status"] == "1":
        return data["result"]
    else:
        return []

def calculate_features(transactions, wallet):
    total_in = 0
    total_out = 0
    tx_count = len(transactions)
    failed_tx = sum(1 for tx in transactions if tx["isError"] == "1")

    for tx in transactions:
        value = int(tx["value"]) / 1e18
        if tx["to"].lower() == wallet.lower():
            total_in += value
        else:
            total_out += value

    return tx_count, total_in, total_out, failed_tx

def rule_based_score(tx_count, total_in, total_out, failed_tx):
    score = 1000
    if tx_count < 5:
        score -= 200
    if failed_tx > 2:
        score -= 150
    if total_out > total_in:
        score -= 100
    return max(0, min(1000, score))

# Load data
wallets_df = pd.read_excel("Wallet id.xlsx")
results = []

# Rule-based scoring
for _, row in wallets_df.iterrows():
    wallet = row["wallet_id"]
    print(f"Processing {wallet}")
    txs = fetch_transactions(wallet)
    tx_count, total_in, total_out, failed_tx = calculate_features(txs, wallet)
    score = rule_based_score(tx_count, total_in, total_out, failed_tx)
    results.append({
        "wallet_id": wallet,
        "tx_count": tx_count,
        "total_in": total_in,
        "total_out": total_out,
        "failed_tx": failed_tx,
        "score_rule_based": score
    })
    time.sleep(0.2)

wallet_df = pd.DataFrame(results)

# Model-based scoring using KMeans
features = ["tx_count", "total_in", "total_out", "failed_tx"]
X_scaled = MinMaxScaler().fit_transform(wallet_df[features])

kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
wallet_df["cluster"] = kmeans.fit_predict(X_scaled)
distances = kmeans.transform(X_scaled)
wallet_df["distance_to_safe"] = distances[:, 0]
wallet_df["score_model_based"] = (1 - MinMaxScaler().fit_transform(wallet_df[["distance_to_safe"]])) * 1000
wallet_df["score_model_based"] = wallet_df["score_model_based"].astype(int)

# PCA and visualize clusters
pca = PCA(n_components=2)
reduced = pca.fit_transform(X_scaled)
wallet_df["pca1"] = reduced[:, 0]
wallet_df["pca2"] = reduced[:, 1]

plt.figure(figsize=(8, 6))
for label in wallet_df["cluster"].unique():
    cluster_data = wallet_df[wallet_df["cluster"] == label]
    plt.scatter(cluster_data["pca1"], cluster_data["pca2"], label=f"Cluster {label}", alpha=0.7)

plt.title("KMeans Clustering of Wallets (PCA 2D View)")
plt.xlabel("PCA 1")
plt.ylabel("PCA 2")
plt.legend()
plt.savefig("kmeans_cluster_visualization.png")

# Save final CSV
wallet_df[["wallet_id", "score_rule_based", "score_model_based"]].to_csv("wallet_risk_scores_combined.csv", index=False)
print("Scoring completed and results saved.")
