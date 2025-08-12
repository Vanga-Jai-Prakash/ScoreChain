import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the clustered data
df = pd.read_csv("kmeans_scored_wallets.csv")

# OPTIONAL: Remove extreme outliers to make plot clearer
df_filtered = df[df["total_txns"] < 1000]  # Remove extreme outliers

# Create the violin plot
plt.figure(figsize=(10, 6))
sns.violinplot(data=df_filtered, x="cluster", y="total_txns", palette="Set2")

plt.title("Distribution of Total Transactions per KMeans Cluster (Capped)")
plt.xlabel("Cluster")
plt.ylabel("Total Transactions")

# Cap the Y-axis to make the scale readable (optional tweak)
plt.ylim(0, 1000)

plt.tight_layout()
plt.savefig("cluster_vs_total_txns_capped.png")
plt.show()
