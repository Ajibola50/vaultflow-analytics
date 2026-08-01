SELECT
    user_id,
    full_name,
    email,
    phone_number,
    bvn,
    nin,
    kyc_tier,
    date_of_birth,
    LOWER(TRIM(state)) AS state,
    signup_date,
    kyc_verified_at,
    LOWER(account_status) AS account_status
FROM {{ source('raw', 'raw_users') }}