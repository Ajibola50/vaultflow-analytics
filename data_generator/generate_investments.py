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

def generate_investments():
    transacting_users = fetch_transacting_users()
    investors = random.sample(transacting_users, int(len(transacting_users) * 0.25))

    investment_types = ["mutual_fund", "fixed_income", "dollar_fund", "treasury_bills"]
    investments = []
    inv_num = 1

    for user_id in investors:
        num_investments = random.choices([1, 2, 3, 4], weights=[35, 30, 20, 15])[0]
        for _ in range(num_investments):
            investment_id = f"INV-{inv_num:05d}"
            inv_num += 1
            investment_type = random.choice(investment_types)
            currency = "USD" if investment_type == "dollar_fund" else "NGN"
            purchase_date = fake.date_between(start_date="-2y", end_date="today")
            status = random.choices(["active", "matured", "withdrawn"], weights=[60, 30, 10])[0]

            amount_invested = round(random.uniform(50, 5000), 2) if currency == "USD" else round(random.uniform(20000, 3000000), 2)

            # units_purchased applies mainly to fund-type investments, null for fixed income/treasury bills
            units_purchased = round(random.uniform(1, 500), 4) if investment_type in ["mutual_fund", "dollar_fund"] else None

            maturity_date = purchase_date + timedelta(days=random.randint(90, 1095)) if investment_type != "mutual_fund" else None

            investments.append({
                "investment_id": investment_id,
                "user_id": user_id,
                "investment_type": investment_type,
                "amount_invested": amount_invested,
                "currency": currency,
                "units_purchased": units_purchased,
                "purchase_date": purchase_date,
                "maturity_date": maturity_date,
                "status": status
            })

    return investments

def insert_investments(investments):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for i in investments:
        cur.execute("""
            INSERT INTO raw_investments (
                investment_id, user_id, investment_type, amount_invested, currency,
                units_purchased, purchase_date, maturity_date, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            i["investment_id"], i["user_id"], i["investment_type"], i["amount_invested"],
            i["currency"], i["units_purchased"], i["purchase_date"], i["maturity_date"], i["status"]
        ))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(investments)} investments into raw_investments.")

if __name__ == "__main__":
    data = generate_investments()
    print(f"Generated {len(data)} investments.")
    print(data[0])
    insert_investments(data)