from prefect import flow, task
import subprocess
import sys

@task
def generate_data():
    scripts = [
        "data_generator/generate_users.py",
        "data_generator/generate_transactions.py",
        "data_generator/generate_savings_plans.py",
        "data_generator/generate_investments.py",
        "data_generator/generate_wallets.py",
        "data_generator/generate_referrals.py",
    ]
    for script in scripts:
        subprocess.run([sys.executable, script], check=True)

@task
def ingest_to_bigquery():
    subprocess.run([sys.executable, "ingestion/postgres_to_bigquery.py"], check=True)

@task
def run_dbt():
    subprocess.run(
        ["dbt", "run"],
        cwd="dbt_project/vaultflow",
        check=True
    )

@task
def test_dbt():
    subprocess.run(
        ["dbt", "test"],
        cwd="dbt_project/vaultflow",
        check=True
    )

@flow(name="vaultflow-pipeline")
def vaultflow_pipeline():
    generate_data()
    ingest_to_bigquery()
    run_dbt()
    test_dbt()

if __name__ == "__main__":
    vaultflow_pipeline()