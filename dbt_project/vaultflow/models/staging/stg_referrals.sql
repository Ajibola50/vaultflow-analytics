SELECT
    referral_id,
    referrer_user_id,
    referred_user_id,
    referral_date,
    reward_amount,
    LOWER(reward_status) AS reward_status
FROM {{ source('raw', 'raw_referrals') }}