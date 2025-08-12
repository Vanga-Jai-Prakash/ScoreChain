
# ScoreChain Wallet Scoring

This project provides an end-to-end pipeline for evaluating wallet creditworthiness using historical DeFi transaction data from the Aave V2 protocol.

## 🧠 Objective

To assign a **credit score (0–1000)** to each wallet based on its on-chain activity (deposit, borrow, repay, liquidation, etc.). Higher scores indicate responsible behavior, while lower scores suggest potential risk or exploitation.

---

## 🛠️ Architecture & Flow

### 1. **Input**
- JSON file of raw Aave V2 transactions per wallet

### 2. **Processing Pipeline**
- Extract relevant metrics per wallet
- Normalize transaction amounts in USD
- Derive behavioral features:
  - Total deposits, borrows, repayments, redemptions
  - Repayment-to-borrow ratio
  - Count of liquidations
  - Time active on the protocol
  - Total number of transactions

### 3.uses a Heuristic Scoring Model: **Scoring Logic**
- We extract key behavioral features from each wallet (e.g., deposits, borrows, liquidations)
- Use `MinMaxScaler` to normalize feature values
- Compute the mean score across features
- Scale to a 0–1000 range
- Output final `score` per wallet

---

## 💾 Output Files

- `scored_wallets.csv`: Contains userWallet and assigned score
- `score_distribution.png`: Bar chart of score ranges
- `analysis.md`: Summary of score distributions and wallet behaviors

---


## 📊 Feature Importance (Heuristics)

- **Repay/Borrow Ratio**: A higher value indicates responsible loan handling
- **Liquidation Count**: More liquidations imply riskier behavior
- **Active Days**: Longer activity may signal legitimacy
- **Transaction Count**: High volume with balanced actions signals healthy engagement

---

## 🧪 Usage

You can re-run the pipeline using:

```bash
python score_wallets.py
```
##🎯 Why This Approach?
- The assignment does not provide labeled data (i.e., no "ground truth" credit scores).
- Without labels, supervised ML models can’t be trained.
- So we rely on rule-based heuristics and domain-driven feature weighting.

##⚙️ Could We Use an ML Model?
🧪Unsupervised ML:
- Use clustering algorithms (e.g., KMeans, DBSCAN) to group wallets by behavior.
- Assign scores based on cluster centroids or ranks.
- To make violin plot more readable (since it's being stretched by extreme outliers), you can cap the y-axis or filter out extreme values.

## 💾 Output Files
- `KMeans Scored Wallets CSV`
- `KMeans Clusters PCA Plot`
- `Cluster vs Total Transactions Violin Plot`
- `cluster_vs_total_txns_capped`
- `KMeans Visualizer Python Script`

## 🧪 Usage

You can re-run the pipeline using:

```bash
python full_kmeans_wallet_pipeline.py
python cluster_vs_total_txns.py
```

Make sure the input JSON is structured like:

```json
[
  {
    "userWallet": "0x123...",
    "action": "deposit",
    "actionData": {
      "amount": "...",
      "assetPriceUSD": "..."
    },
    "timestamp": 1629178166
  },
  ...
]
```

---

## 📌 Notes

- This scoring is heuristic and unsupervised.
- It is not financial advice and should be further calibrated before production use.

---

## 📧 Contact

For questions or contributions, reach out via GitHub or email.
