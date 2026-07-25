import random
import psycopg2
from datetime import timedelta
from faker import Faker

fake = Faker("en_US")

DB_CONFIG = dict(
    host="localhost", port=5432, dbname="vaultflow",
    user="vaultflow_admin", password="changeme_dev_only"
)

def fetch_transacting_users():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT user_id FROM raw_transactions;")
    rows = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

def generate_referrals():
    transacting_users = fetch_transacting_users()
    referrers = random.sample(transacting_users, int(len(transacting_users) * 0.25))

    referrals = []
    ref_num = 1

    for referrer in referrers:
        num_referrals = random.choices([1, 2], weights=[70, 30])[0]
        for _ in range(num_referrals):
            referral_id = f"REF-{ref_num:05d}"
            ref_num += 1

            roll = random.random()
            if roll < 0.02:
                # deliberate mess: self-referral (fraud signal)
                referred = referrer
            elif roll < 0.05:
                # deliberate mess: orphaned foreign key - references a user_id that doesn't exist
                referred = f"USR-{random.randint(90000, 99999)}"
            else:
                referred = random.choice(transacting_users)

            reward_status = random.choices(["pending", "paid", "forfeited"], weights=[20, 70, 10])[0]
            reward_amount = None if reward_status == "pending" and random.random() < 0.3 else round(random.uniform(200, 1000), 2)

            referrals.append({
                "referral_id": referral_id,
                "referrer_user_id": referrer,
                "referred_user_id": referred,
                "referral_date": fake.date_between(start_date="-2y", end_date="today"),
                "reward_amount": reward_amount,
                "reward_status": reward_status
            })

    return referrals

def insert_referrals(referrals):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for r in referrals:
        try:
            cur.execute("""
                INSERT INTO raw_referrals (
                    referral_id, referrer_user_id, referred_user_id,
                    referral_date, reward_amount, reward_status
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                r["referral_id"], r["referrer_user_id"], r["referred_user_id"],
                r["referral_date"], r["reward_amount"], r["reward_status"]
            ))
        except psycopg2.errors.ForeignKeyViolation:
            conn.rollback()  # skip rows that violate FK (the deliberately orphaned ones)
            continue
        conn.commit()
    cur.close()
    conn.close()
    print(f"Attempted {len(referrals)} referrals into raw_referrals.")

if __name__ == "__main__":
    data = generate_referrals()
    print(f"Generated {len(data)} referrals.")
    print(data[0])
    insert_referrals(data)