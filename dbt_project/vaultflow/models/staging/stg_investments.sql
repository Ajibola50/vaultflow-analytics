SELECT
    investment_id,
    user_id,
    LOWER(investment_type) AS investment_type,
    amount_invested,
    currency,
    units_purchased,
    purchase_date,
    maturity_date,
    LOWER(status) AS status
FROM {{ source('raw', 'raw_investments') }}