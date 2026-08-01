SELECT
    plan_id,
    user_id,
    LOWER(plan_type) AS plan_type,
    target_amount,
    principal_amount,
    interest_rate,
    start_date,
    maturity_date,
    LOWER(status) AS status
FROM {{ source('raw', 'raw_savings_plans') }}