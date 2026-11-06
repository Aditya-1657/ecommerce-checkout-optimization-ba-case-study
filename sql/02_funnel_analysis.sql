-- ============================================================
-- Checkout funnel analysis  |  table: checkout_sessions
-- ============================================================

-- Q1. Overall funnel: sessions reaching each step, drop-off and step conversion
WITH steps AS (
    SELECT 1 AS step_no, 'Cart' AS step_name UNION ALL
    SELECT 2, 'Login / Create Account' UNION ALL
    SELECT 3, 'Shipping Address' UNION ALL
    SELECT 4, 'Delivery Options' UNION ALL
    SELECT 5, 'Payment Details' UNION ALL
    SELECT 6, 'Gateway Authorisation' UNION ALL
    SELECT 7, 'Order Confirmed'
),
reached AS (
    SELECT s.step_no, s.step_name,
           COUNT(c.session_id) AS sessions_reached
    FROM steps s
    LEFT JOIN checkout_sessions c ON c.last_step_reached >= s.step_no
    GROUP BY s.step_no, s.step_name
)
SELECT step_no,
       step_name,
       sessions_reached,
       LAG(sessions_reached) OVER (ORDER BY step_no) - sessions_reached      AS sessions_lost_before_this_step,
       ROUND(100.0 * sessions_reached /
             LAG(sessions_reached) OVER (ORDER BY step_no), 1)                AS step_conversion_pct,
       ROUND(100.0 * sessions_reached /
             FIRST_VALUE(sessions_reached) OVER (ORDER BY step_no), 1)        AS cumulative_conversion_pct
FROM reached
ORDER BY step_no;


-- Q2. Where do sessions exit? (count, share of all exits, lost cart value)
SELECT last_step_reached                                   AS exit_step,
       last_step_name,
       COUNT(*)                                            AS sessions_lost,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)  AS pct_of_all_exits,
       ROUND(SUM(cart_value_usd), 0)                       AS lost_cart_value_usd,
       ROUND(AVG(cart_value_usd), 2)                       AS avg_lost_cart_usd
FROM checkout_sessions
WHERE converted = 0
GROUP BY last_step_reached, last_step_name
ORDER BY last_step_reached;


-- Q3. Payment stage (steps 5 and 6) combined, as a share of sessions that reached payment
SELECT COUNT(*)                                                       AS reached_payment,
       SUM(CASE WHEN converted = 0 THEN 1 ELSE 0 END)                 AS lost_in_payment,
       ROUND(100.0 * SUM(CASE WHEN converted = 0 THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                           AS payment_abandon_pct,
       ROUND(SUM(CASE WHEN converted = 0 THEN cart_value_usd END), 0) AS lost_value_usd
FROM checkout_sessions
WHERE last_step_reached >= 5;


-- Q4. Device split: conversion at gateway authorisation (step 6 -> 7)
SELECT device_type,
       SUM(CASE WHEN last_step_reached >= 6 THEN 1 ELSE 0 END)                 AS reached_gateway,
       SUM(CASE WHEN last_step_reached = 7 THEN 1 ELSE 0 END)                  AS completed,
       ROUND(100.0 * SUM(CASE WHEN last_step_reached = 7 THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN last_step_reached >= 6 THEN 1 ELSE 0 END), 0), 1) AS gateway_pass_pct,
       ROUND(100.0 * SUM(converted) / COUNT(*), 1)                             AS overall_conversion_pct
FROM checkout_sessions
GROUP BY device_type
ORDER BY overall_conversion_pct DESC;


-- Q5. Why do people leave at the gateway? (exit tags captured by the app)
SELECT exit_tag,
       COUNT(*)                                            AS sessions,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)  AS pct_of_gateway_exits,
       ROUND(SUM(cart_value_usd), 0)                       AS lost_value_usd
FROM checkout_sessions
WHERE last_step_reached = 6 AND converted = 0
GROUP BY exit_tag
ORDER BY sessions DESC;


-- Q6. Forced account creation: new vs returning customers at step 2 -> 3
SELECT customer_type,
       SUM(CASE WHEN last_step_reached >= 2 THEN 1 ELSE 0 END) AS reached_login_step,
       SUM(CASE WHEN last_step_reached >= 3 THEN 1 ELSE 0 END) AS moved_on,
       ROUND(100.0 * SUM(CASE WHEN last_step_reached >= 3 THEN 1 ELSE 0 END)
             / SUM(CASE WHEN last_step_reached >= 2 THEN 1 ELSE 0 END), 1) AS step_pass_pct
FROM checkout_sessions
GROUP BY customer_type;


-- Q7. Does a slow payment page hurt? (load-time buckets, step 5 -> 6)
SELECT CASE WHEN payment_page_load_sec < 3 THEN '1) under 3s'
            WHEN payment_page_load_sec < 4.5 THEN '2) 3 to 4.5s'
            ELSE '3) over 4.5s' END                                    AS load_bucket,
       SUM(CASE WHEN last_step_reached >= 5 THEN 1 ELSE 0 END)         AS reached_payment,
       SUM(CASE WHEN last_step_reached >= 6 THEN 1 ELSE 0 END)         AS submitted_payment,
       ROUND(100.0 * SUM(CASE WHEN last_step_reached >= 6 THEN 1 ELSE 0 END)
             / SUM(CASE WHEN last_step_reached >= 5 THEN 1 ELSE 0 END), 1) AS step_pass_pct
FROM checkout_sessions
GROUP BY 1
ORDER BY 1;


-- Q8. Shipping cost reveal: step 4 -> 5 for free vs paid shipping
SELECT CASE WHEN shipping_cost_usd = 0 THEN 'Free shipping' ELSE 'Paid shipping' END AS shipping_type,
       SUM(CASE WHEN last_step_reached >= 4 THEN 1 ELSE 0 END) AS reached_delivery,
       SUM(CASE WHEN last_step_reached >= 5 THEN 1 ELSE 0 END) AS moved_to_payment,
       ROUND(100.0 * SUM(CASE WHEN last_step_reached >= 5 THEN 1 ELSE 0 END)
             / SUM(CASE WHEN last_step_reached >= 4 THEN 1 ELSE 0 END), 1) AS step_pass_pct
FROM checkout_sessions
GROUP BY 1;


-- Q9. Weekly conversion trend (is the problem new or constant?)
SELECT STRFTIME('%Y-W%W', session_date)          AS year_week,   -- PostgreSQL: TO_CHAR(session_date,'IYYY-"W"IW')
       COUNT(*)                                  AS sessions,
       ROUND(100.0 * SUM(converted) / COUNT(*), 1) AS conversion_pct
FROM checkout_sessions
GROUP BY 1
ORDER BY 1;
