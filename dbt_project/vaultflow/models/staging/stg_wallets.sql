SELECT
    wallet_id,
    user_id,
    currency,
    balance,
    last_updated_at
FROM {{ source('raw', 'raw_wallets') }}