SELECT
    transaction_id,
    user_id,
    amount,
    transaction_type,
    status,
    channel,
    flagged_for_review,
    kyc_tier,
    tier_limit,
    breached_tier_limit,
    created_at
FROM {{ ref('int_transactions_with_kyc_check') }}