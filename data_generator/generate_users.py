from faker import Faker
import random
import psycopg2
from datetime import datetime, timedelta

fake = Faker("en_US")  # kept only for dates; names/emails/phones are custom

yoruba_first = ["Ade", "Bimpe", "Bukola", "Damilola", "Folake", "Femi", "Kunle",
                 "Ayodele", "Yemi", "Segun", "Kemi", "Tolu", "Wale", "Tunde", "Bola",
                 "Adeola", "Tobi", "Sade", "Gbenga", "Funmi"]
yoruba_last = ["Adeyemi", "Balogun", "Ogunleye", "Afolabi", "Alade", "Ajayi",
               "Adebayo", "Bakare", "Fashola", "Ogunyemi", "Babatunde", "Adewale"]

igbo_first = ["Chidinma", "Chinedu", "Emeka", "Ngozi", "Ifeoma", "Obinna", "Amaka",
              "Uche", "Chioma", "Chukwuemeka", "Nnamdi", "Adaeze", "Kelechi",
              "Chiamaka", "Ikenna", "Onyeka", "Ebele", "Chibuzo"]
igbo_last = ["Okoye", "Eze", "Okafor", "Nwosu", "Chukwu", "Okonkwo",
             "Uzoma", "Obi", "Anyanwu", "Nwachukwu", "Madu"]

hausa_first = ["Ibrahim", "Aisha", "Musa", "Fatima", "Aliyu", "Zainab", "Suleiman",
               "Amina", "Yusuf", "Hauwa", "Abubakar", "Halima", "Sani", "Maryam"]
hausa_last = ["Abubakar", "Bello", "Suleiman", "Yusuf", "Ibrahim", "Sani",
              "Mohammed", "Garba", "Idris", "Tanko"]

ethnic_groups = {
    "yoruba": (yoruba_first, yoruba_last),
    "igbo": (igbo_first, igbo_last),
    "hausa": (hausa_first, hausa_last),
}

email_domains = ["gmail.com", "yahoo.com", "outlook.com"]
network_prefixes = ["0803", "0805", "0806", "0810", "0813", "0814", "0816",
                     "0703", "0706", "0802", "0808", "0812",
                     "0705", "0807", "0815", "0811",
                     "0809", "0817", "0818", "0908", "0909"]

def generate_name():
    if random.random() < 0.90:
        group = random.choice(list(ethnic_groups.keys()))
        first_list, last_list = ethnic_groups[group]
        first = random.choice(first_list)
        last = random.choice(last_list)
    else:
        first_group = random.choice(list(ethnic_groups.keys()))
        last_group = random.choice(list(ethnic_groups.keys()))
        first = random.choice(ethnic_groups[first_group][0])
        last = random.choice(ethnic_groups[last_group][1])
    return first, last

def generate_email(first, last):
    domain = random.choice(email_domains)
    style = random.choice([
        f"{first.lower()}.{last.lower()}",
        f"{first.lower()}{last.lower()}",
        f"{first.lower()}{random.randint(1,999)}",
    ])
    return f"{style}@{domain}"

def generate_phone():
    prefix = random.choice(network_prefixes)
    remainder = fake.numerify("#######")
    return f"{prefix}{remainder}"

def generate_users(n=5000):
    users = []

    state_weights = {
        "Lagos": 35, "FCT Abuja": 15, "Rivers": 8, "Oyo": 7, "Kano": 6,
        "Ogun": 4, "Kaduna": 3, "Delta": 3, "Enugu": 3, "Anambra": 3,
        "Edo": 2, "Plateau": 2, "Cross River": 2, "Kwara": 2,
        "Abia": 1, "Imo": 1, "Osun": 1, "Ondo": 1, "Akwa Ibom": 1
    }
    states = list(state_weights.keys())
    weights = list(state_weights.values())

    for i in range(n):
        user_id = f"USR-{i+1:05d}"
        first, last = generate_name()
        signup_date = fake.date_time_between(start_date="-2y", end_date="now")
        kyc_verified = random.random() < 0.80

        users.append({
            "user_id": user_id,
            "full_name": f"{first} {last}",
            "email": generate_email(first, last),
            "phone_number": generate_phone(),
            "bvn": fake.numerify("###########") if kyc_verified else None,
            "nin": fake.numerify("###########") if kyc_verified else None,
            "kyc_tier": random.choice([1, 2, 3]) if kyc_verified else 1,
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=65),
            "state": random.choices(states, weights=weights)[0],
            "signup_date": signup_date,
            "kyc_verified_at": signup_date + timedelta(days=random.randint(1, 14)) if kyc_verified else None,
            "account_status": random.choices(["active", "dormant", "suspended"], weights=[85, 12, 3])[0]
        })

    return users

def insert_users(users):
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="vaultflow",
        user="vaultflow_admin",
        password="changeme_dev_only"
    )
    cur = conn.cursor()

    for u in users:
        cur.execute("""
            INSERT INTO raw_users (
                user_id, full_name, email, phone_number, bvn, nin,
                kyc_tier, date_of_birth, state, signup_date,
                kyc_verified_at, account_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            u["user_id"], u["full_name"], u["email"], u["phone_number"],
            u["bvn"], u["nin"], u["kyc_tier"], u["date_of_birth"],
            u["state"], u["signup_date"], u["kyc_verified_at"], u["account_status"]
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(users)} users into raw_users.")

if __name__ == "__main__":
    data = generate_users()
    print(f"Generated {len(data)} users.")
    insert_users(data)