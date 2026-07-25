import random
import psycopg2
from datetime import datetime

DB_CONFIG = dict(
    host="localhost", port=5432, dbname="vaultflow",
    user="vaultflow_admin", password="changeme_dev_only"
)

def fetch_all_users():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM raw_users;")
    rows = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

def fetch_usd_investors():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT user_id FROM raw_investments WHERE currency = 'USD';")
    rows = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

def generate_wallets():
    all_users = fetch_all_users()
    usd_investors = set(fetch_usd_investors())

    wallets = []
    wallet_num = 1

    for user_id in all_users:
        wallet_id = f"WLT-{wallet_num:05d}"
        wallet_num += 1
        wallets.append({
            "wallet_id": wallet_id,
            "user_id": user_id,
            "currency": "NGN",
            "balance": round(random.uniform(0, 500000), 2),
            "last_updated_at": datetime.now()
        })

        if user_id in usd_investors:
            wallet_id = f"WLT-{wallet_num:05d}"
            wallet_num += 1
            wallets.append({
                "wallet_id": wallet_id,
                "user_id": user_id,
                "currency": "USD",
                "balance": round(random.uniform(0, 2000), 2),
                "last_updated_at": datetime.now()
            })

    return wallets

def insert_wallets(wallets):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for w in wallets:
        cur.execute("""
            INSERT INTO raw_wallets (
                wallet_id, user_id, currency, balance, last_updated_at
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            w["wallet_id"], w["user_id"], w["currency"], w["balance"], w["last_updated_at"]
        ))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(wallets)} wallets into raw_wallets.")

if __name__ == "__main__":
    data = generate_wallets()
    print(f"Generated {len(data)} wallets.")
    print(data[0])
    insert_wallets(data)