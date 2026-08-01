SELECT
    transaction_id,
    user_id,
    LOWER(transaction_type) AS transaction_type,
    amount,
    currency,
    LOWER(status) AS status,
    LOWER(channel) AS channel,
    narration,
    flagged_for_review,
    created_at
FROM {{ source('raw', 'raw_transactions') }}