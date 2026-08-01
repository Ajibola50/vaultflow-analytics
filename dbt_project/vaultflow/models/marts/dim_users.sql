SELECT
    user_id,
    full_name,
    email,
    phone_number,
    kyc_tier,
    date_of_birth,
    state,
    signup_date,
    kyc_verified_at,
    account_status
FROM {{ ref('stg_users') }}