from fastapi import FastAPI, HTTPException
import psycopg2
from api.models import UserCreate

app = FastAPI()

DB_CONFIG = dict(
    host="localhost", port=5432, dbname="vaultflow",
    user="vaultflow_admin", password="changeme_dev_only"
)

@app.post("/users")
def create_user(user: UserCreate):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO raw_users (
                user_id, full_name, email, phone_number, bvn, nin,
                kyc_tier, date_of_birth, state, signup_date,
                kyc_verified_at, account_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user.user_id, user.full_name, user.email, user.phone_number,
            user.bvn, user.nin, user.kyc_tier, user.date_of_birth,
            user.state, user.signup_date, user.kyc_verified_at, user.account_status
        ))
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="user_id already exists")
    finally:
        cur.close()
        conn.close()

    return {"message": "User created", "user_id": user.user_id}