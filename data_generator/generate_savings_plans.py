from faker import Faker
import random
import psycopg2
from datetime import timedelta

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

def generate_savings_plans():
    transacting_users = fetch_transacting_users()
    savers = random.sample(transacting_users, int(len(transacting_users) * 0.60))

    plan_types = ["fixed", "flexible", "target"]
    plans = []
    plan_num = 1

    for user_id in savers:
        num_plans = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10])[0]
        for _ in range(num_plans):
            plan_id = f"PLN-{plan_num:05d}"
            plan_num += 1
            plan_type = random.choice(plan_types)
            start_date = fake.date_between(start_date="-2y", end_date="today")
            status = random.choices(
                ["active", "matured", "broken", "closed"],
                weights=[55, 25, 12, 8]
            )[0]

            # only "target" plans have a target_amount; others are None
            target_amount = round(random.uniform(50000, 2000000), 2) if plan_type == "target" else None

            # maturity_date only makes sense if plan isn't still open-ended/"flexible"
            maturity_date = start_date + timedelta(days=random.randint(90, 730)) if plan_type != "flexible" else None

            plans.append({
                "plan_id": plan_id,
                "user_id": user_id,
                "plan_type": plan_type,
                "target_amount": target_amount,
                "principal_amount": round(random.uniform(10000, 1000000), 2),
                "interest_rate": round(random.uniform(2.0, 15.0), 2),
                "start_date": start_date,
                "maturity_date": maturity_date,
                "status": status
            })

    return plans

def insert_savings_plans(plans):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for p in plans:
        cur.execute("""
            INSERT INTO raw_savings_plans (
                plan_id, user_id, plan_type, target_amount, principal_amount,
                interest_rate, start_date, maturity_date, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            p["plan_id"], p["user_id"], p["plan_type"], p["target_amount"],
            p["principal_amount"], p["interest_rate"], p["start_date"],
            p["maturity_date"], p["status"]
        ))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(plans)} savings plans into raw_savings_plans.")

if __name__ == "__main__":
    data = generate_savings_plans()
    print(f"Generated {len(data)} savings plans.")
    print(data[0])
    insert_savings_plans(data)