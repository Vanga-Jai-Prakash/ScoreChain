
import json
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

def load_transactions(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def process_transactions(data):
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df['usd_value'] = df.apply(lambda row: float(row['actionData'].get('amount', 0)) *
                               float(row['actionData'].get('assetPriceUSD', 0)), axis=1)

    wallets = defaultdict(lambda: {
        'total_txns': 0,
        'deposit_usd': 0,
        'borrow_usd': 0,
        'repay_usd': 0,
        'redeem_usd': 0,
        'liquidations': 0,
        'first_seen': None,
        'last_seen': None
    })

    for _, row in df.iterrows():
        wallet = row['userWallet']
        action = row['action'].lower()
        usd_value = row['usd_value']
        ts = row['timestamp']

        wallets[wallet]['total_txns'] += 1
        if action == 'deposit':
            wallets[wallet]['deposit_usd'] += usd_value
        elif action == 'borrow':
            wallets[wallet]['borrow_usd'] += usd_value
        elif action == 'repay':
            wallets[wallet]['repay_usd'] += usd_value
        elif action == 'redeemunderlying':
            wallets[wallet]['redeem_usd'] += usd_value
        elif action == 'liquidationcall':
            wallets[wallet]['liquidations'] += 1

        if wallets[wallet]['first_seen'] is None or ts < wallets[wallet]['first_seen']:
            wallets[wallet]['first_seen'] = ts
        if wallets[wallet]['last_seen'] is None or ts > wallets[wallet]['last_seen']:
            wallets[wallet]['last_seen'] = ts

    wallet_data = []
    for wallet, stats in wallets.items():
        active_days = (stats['last_seen'] - stats['first_seen']).days or 1
        repay_borrow_ratio = stats['repay_usd'] / stats['borrow_usd'] if stats['borrow_usd'] else 0
        wallet_data.append({
            'userWallet': wallet,
            'total_txns': stats['total_txns'],
            'deposit_usd': stats['deposit_usd'],
            'borrow_usd': stats['borrow_usd'],
            'repay_usd': stats['repay_usd'],
            'redeem_usd': stats['redeem_usd'],
            'liquidations': stats['liquidations'],
            'active_days': active_days,
            'repay_borrow_ratio': repay_borrow_ratio
        })

    return pd.DataFrame(wallet_data)

def score_wallets(df_wallets):
    features = ['deposit_usd', 'borrow_usd', 'repay_usd', 'redeem_usd',
                'repay_borrow_ratio', 'active_days', 'total_txns']
    scaler = MinMaxScaler()
    df_wallets['score'] = scaler.fit_transform(df_wallets[features]).mean(axis=1) * 1000
    df_wallets['score'] = df_wallets['score'].round().astype(int)
    return df_wallets

def plot_distribution(df_wallets, output_path):
    score_bins = pd.cut(df_wallets['score'], bins=range(0, 1100, 100))
    distribution = score_bins.value_counts().sort_index()
    plt.figure(figsize=(10, 6))
    distribution.plot(kind='bar')
    plt.title("Wallet Score Distribution")
    plt.xlabel("Score Range")
    plt.ylabel("Number of Wallets")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Score distribution plot saved to {output_path}")

def main():
    json_file = "user_wallet_data/user-wallet-transactions.json"
    data = load_transactions(json_file)
    df_wallets = process_transactions(data)
    df_wallets = score_wallets(df_wallets)
    df_wallets.to_csv("scored_wallets.csv", index=False)
    plot_distribution(df_wallets, "score_distribution.png")
    print("Scoring completed. Results saved to 'scored_wallets.csv'.")

if __name__ == "__main__":
    main()
