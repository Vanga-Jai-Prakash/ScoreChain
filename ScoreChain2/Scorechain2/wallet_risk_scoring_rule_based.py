import requests
import pandas as pd
import time

ETHERSCAN_API_KEY = "YOUR_ETHERSCAN_API_KEY"  # <-- Replace this

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

def calculate_features(transactions):
    total_in = 0
    total_out = 0
    tx_count = len(transactions)
    failed_tx = sum(1 for tx in transactions if tx["isError"] == "1")
    
    for tx in transactions:
        value = int(tx["value"]) / 1e18  # Convert Wei to ETH
        if tx["to"].lower() == wallet.lower():
            total_in += value
        else:
            total_out += value

    return tx_count, total_in, total_out, failed_tx

def calculate_risk_score(tx_count, total_in, total_out, failed_tx):
    score = 1000
    if tx_count < 5:
        score -= 200
    if failed_tx > 2:
        score -= 150
    if total_out > total_in:
        score -= 100
    return max(0, min(1000, score))

# Load wallet addresses
wallets_df = pd.read_excel("Wallet_id.xlsx")
results = []

for index, row in wallets_df.iterrows():
    wallet = row["wallet_id"]
    print(f"Processing: {wallet}")
    txs = fetch_transactions(wallet)
    tx_count, total_in, total_out, failed_tx = calculate_features(txs)
    score = calculate_risk_score(tx_count, total_in, total_out, failed_tx)
    results.append({
        "wallet_id": wallet,
        "score": score
    })
    time.sleep(0.2)  # to avoid rate limiting

# Save results
output_df = pd.DataFrame(results)
output_df.to_csv("wallet_risk_scores_rule_based.csv", index=False)
print("Saved to wallet_risk_scores_rule_based.csv")