from faker import Faker
import random
import numpy as np
import psycopg2
from datetime import timedelta

fake = Faker("en_US")

DB_CONFIG = dict(
    host="localhost", port=5432, dbname="vaultflow",
    user="vaultflow_admin", password="changeme_dev_only"
)

def fetch_users():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT user_id, signup_date, kyc_verified_at FROM raw_users;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows  # list of (user_id, signup_date, kyc_verified_at)

def generate_transactions(target_total=50000):
    users = fetch_users()

    # only users who are verified (or unverified Tier 1, per CBN rules) can transact
    # here: 90% of verified users transact; a small 10% of unverified also do (basic tier)
    eligible = []
    for user_id, signup_date, kyc_verified_at in users:
        if kyc_verified_at is not None and random.random() < 0.90:
            eligible.append((user_id, signup_date))
        elif kyc_verified_at is None and random.random() < 0.10:
            eligible.append((user_id, signup_date))

    # long-tail distribution: most users transact a little, a few transact a lot
    # numpy's Pareto distribution naturally creates this "few do most of it" shape
    raw_weights = np.random.pareto(a=2.0, size=len(eligible)) + 1
    weights = raw_weights / raw_weights.sum()
    counts = (weights * target_total).astype(int)

    types = ["deposit", "withdrawal", "transfer", "savings_contribution"]
    channels = ["app", "ussd", "web", "api"]
    transactions = []
    txn_num = 1

    for (user_id, signup_date), count in zip(eligible, counts):
        for _ in range(count):
            txn_id = f"TXN-{txn_num:06d}"
            txn_num += 1
            created_at = fake.date_time_between(start_date=signup_date, end_date="now")
            status = random.choices(
                ["success", "failed", "pending", "reversed"],
                weights=[85, 8, 5, 2]
            )[0]
            transactions.append({
                "transaction_id": txn_id,
                "user_id": user_id,
                "transaction_type": random.choice(types),
                "amount": round(random.uniform(500, 500000), 2),
                "currency": "NGN",
                "status": status,
                "channel": random.choice(channels),
                "narration": None if random.random() < 0.2 else fake.sentence(nb_words=4),
                "flagged_for_review": random.random() < 0.02,  # 2% AML-relevant signal
                "created_at": created_at
            })

    return transactions

def insert_transactions(transactions):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for t in transactions:
        cur.execute("""
            INSERT INTO raw_transactions (
                transaction_id, user_id, transaction_type, amount, currency,
                status, channel, narration, flagged_for_review, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            t["transaction_id"], t["user_id"], t["transaction_type"], t["amount"],
            t["currency"], t["status"], t["channel"], t["narration"],
            t["flagged_for_review"], t["created_at"]
        ))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(transactions)} transactions into raw_transactions.")

if __name__ == "__main__":
    data = generate_transactions()
    print(f"Generated {len(data)} transactions.")
    print(data[0])
    insert_transactions(data)