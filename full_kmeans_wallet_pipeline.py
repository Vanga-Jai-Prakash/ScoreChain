
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import defaultdict

# Load JSON file
with open("user-wallet-transactions.json", "r") as f:
    transactions_data = json.load(f)

# Parse DataFrame
df = pd.DataFrame(transactions_data)
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
df["usd_value"] = df.apply(lambda row: float(row["actionData"].get("amount", 0)) *
                           float(row["actionData"].get("assetPriceUSD", 0)), axis=1)

wallets = defaultdict(lambda: {
    "total_txns": 0, "deposit_usd": 0, "borrow_usd": 0,
    "repay_usd": 0, "redeem_usd": 0, "liquidations": 0,
    "first_seen": None, "last_seen": None
})

for _, row in df.iterrows():
    w, act, val, ts = row["userWallet"], row["action"].lower(), row["usd_value"], row["timestamp"]
    wallets[w]["total_txns"] += 1
    if act == "deposit": wallets[w]["deposit_usd"] += val
    elif act == "borrow": wallets[w]["borrow_usd"] += val
    elif act == "repay": wallets[w]["repay_usd"] += val
    elif act == "redeemunderlying": wallets[w]["redeem_usd"] += val
    elif act == "liquidationcall": wallets[w]["liquidations"] += 1
    if not wallets[w]["first_seen"] or ts < wallets[w]["first_seen"]: wallets[w]["first_seen"] = ts
    if not wallets[w]["last_seen"] or ts > wallets[w]["last_seen"]: wallets[w]["last_seen"] = ts

wallet_data = []
for w, s in wallets.items():
    days = (s["last_seen"] - s["first_seen"]).days or 1
    repay_ratio = s["repay_usd"] / s["borrow_usd"] if s["borrow_usd"] else 0
    wallet_data.append({
        "userWallet": w, "total_txns": s["total_txns"],
        "deposit_usd": s["deposit_usd"], "borrow_usd": s["borrow_usd"],
        "repay_usd": s["repay_usd"], "redeem_usd": s["redeem_usd"],
        "liquidations": s["liquidations"], "active_days": days,
        "repay_borrow_ratio": repay_ratio
    })

df_wallets = pd.DataFrame(wallet_data)

# KMeans and PCA
features = ["deposit_usd", "borrow_usd", "repay_usd", "redeem_usd",
            "repay_borrow_ratio", "active_days", "total_txns"]
X_scaled = MinMaxScaler().fit_transform(df_wallets[features])
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
df_wallets["cluster"] = kmeans.fit_predict(X_scaled)

pca = PCA(n_components=2)
pca_result = pca.fit_transform(X_scaled)
df_wallets["pca1"], df_wallets["pca2"] = pca_result[:, 0], pca_result[:, 1]

# Save CSV
df_wallets.to_csv("kmeans_scored_wallets.csv", index=False)

# Save PCA plot
plt.figure(figsize=(10, 7))
sns.scatterplot(data=df_wallets, x="pca1", y="pca2", hue="cluster", palette="Set1", alpha=0.7)
plt.title("KMeans Clustering of Wallets (PCA Reduced)")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.tight_layout()
plt.savefig("kmeans_clusters_pca.png")

# Save Violin plot
plt.figure(figsize=(10, 6))
sns.violinplot(data=df_wallets, x="cluster", y="total_txns", palette="Set2")
plt.title("Distribution of Total Transactions per KMeans Cluster")
plt.xlabel("Cluster")
plt.ylabel("Total Transactions")
plt.tight_layout()
plt.savefig("cluster_vs_total_txns.png")

print("✅ All files saved: kmeans_scored_wallets.csv, kmeans_clusters_pca.png, cluster_vs_total_txns.png")
