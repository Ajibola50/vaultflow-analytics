SELECT
    t.transaction_id,
    t.user_id,
    t.amount,
    t.transaction_type,
    t.status,
    t.channel,
    t.flagged_for_review,
    t.created_at,
    u.kyc_tier,
    CASE
        WHEN u.kyc_tier = 1 THEN 50000
        WHEN u.kyc_tier = 2 THEN 200000
        WHEN u.kyc_tier = 3 THEN 5000000
    END AS tier_limit,
    CASE
        WHEN u.kyc_tier = 1 AND t.amount > 50000 THEN TRUE
        WHEN u.kyc_tier = 2 AND t.amount > 200000 THEN TRUE
        WHEN u.kyc_tier = 3 AND t.amount > 5000000 THEN TRUE
        ELSE FALSE
    END AS breached_tier_limit
FROM {{ ref('stg_transactions') }} t
JOIN {{ ref('stg_users') }} u
    ON t.user_id = u.user_id