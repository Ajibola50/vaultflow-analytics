import psycopg2
import pandas as pd
from google.cloud import bigquery

PG_CONFIG = dict(
    host="localhost", port=5432, dbname="vaultflow",
    user="vaultflow_admin", password="changeme_dev_only"
)

BQ_PROJECT = "vaultflow-analytics"
BQ_DATASET = "raw"

TABLES = [
    "raw_users",
    "raw_transactions",
    "raw_savings_plans",
    "raw_investments",
    "raw_wallets",
    "raw_referrals"
]

def load_table_to_bigquery(table_name):
    # Step 1: pull the table out of PostgreSQL into a pandas DataFrame
    conn = psycopg2.connect(**PG_CONFIG)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    print(f"Pulled {len(df)} rows from PostgreSQL table '{table_name}'.")

    # Step 2: push that DataFrame into BigQuery
    client = bigquery.Client(project=BQ_PROJECT)
    table_id = f"{BQ_PROJECT}.{BQ_DATASET}.{table_name}"

    job = client.load_table_from_dataframe(df, table_id)
    job.result()  # wait for the load to finish

    print(f"Loaded {len(df)} rows into BigQuery table '{table_id}'.")

if __name__ == "__main__":
    for table in TABLES:
        load_table_to_bigquery(table)
    print("All six tables successfully loaded into BigQuery raw dataset.")