# VaultFlow Analytics

A simulated Nigerian fintech data pipeline — turning messy, regulation-bound raw transaction data into a tested, trustworthy analytics layer for business and compliance decisions.

## The Problem

Nigerian fintechs generate high-volume transactional data that must satisfy two audiences at once: a business team asking "are we growing," and a compliance reviewer asking "can we trust these numbers against CBN regulations." Raw, unmodeled data can't reliably answer either. VaultFlow simulates a savings/investment platform (modeled on Cowrywise/Piggyvest) and builds the full pipeline needed to close that gap.

## Architecture

Python (Faker) → FastAPI → PostgreSQL (OLTP) → BigQuery (raw → staging → intermediate → marts via dbt) → Metabase

## Key Engineering Decisions

- **KYC tier is server-calculated, never client-submitted.** Tier is derived from whether a user has verified `bvn`/`nin` — a real trust-boundary fix applied after initially allowing tier as user input.
- **Referential integrity is enforced at the database level.** Deliberately injected orphaned/self-referencing referral rows are correctly rejected by PostgreSQL's foreign key constraints (43 of 1,202 attempted rows).
- **Realistic funnel-based data volumes**, not flat row counts — 5,000 signups narrowing through KYC verification, transacting, saving, investing, and referring, matching real product adoption behavior.
- **Compliance signal built into the intermediate layer** — `int_transactions_with_kyc_check` joins transactions to users and flags transactions exceeding their KYC tier's allowed limit.
- **dbt tests enforce data quality** — uniqueness, not-null, and relationship tests across the marts layer.

## Dashboards

- **VaultFlow Compliance Dashboard** — KYC tier limit breaches, transaction status health, channel usage, savings plan status
- **VaultFlow Growth & Engagement Dashboard** — signup trends, user growth funnel, referral outcomes, geographic distribution

## Tech Stack

Python, FastAPI, PostgreSQL, Docker, Google BigQuery, dbt, Metabase

## Setup

1. `docker compose up -d` — starts PostgreSQL and Metabase
2. `python data_generator/generate_*.py` — generates and inserts synthetic data
3. `uvicorn api.main:app --reload` — runs the FastAPI backend
4. `python ingestion/postgres_to_bigquery.py` — loads raw data into BigQuery
5. `dbt run` (from `dbt_project/vaultflow`) — builds staging, intermediate, and marts models
6. `dbt test` — runs data quality tests
