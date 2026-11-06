-- Table definition (works in SQLite / PostgreSQL / MySQL with minor type tweaks)
DROP TABLE IF EXISTS checkout_sessions;

CREATE TABLE checkout_sessions (
    session_id               VARCHAR(12) PRIMARY KEY,
    session_date             DATE,
    device_type              VARCHAR(10),
    traffic_source           VARCHAR(20),
    customer_type            VARCHAR(10),
    items_in_cart            INT,
    cart_value_usd           DECIMAL(10,2),
    shipping_cost_usd        DECIMAL(6,2),
    payment_page_load_sec    DECIMAL(4,1),
    last_step_reached        INT,           -- 1..7 (7 = order confirmed)
    last_step_name           VARCHAR(30),
    payment_method_attempted VARCHAR(20),
    exit_tag                 VARCHAR(40),
    gateway_error_flag       INT,
    converted                INT
);

-- PostgreSQL:  \copy checkout_sessions FROM 'data/checkout_sessions.csv' CSV HEADER
-- SQLite CLI:  .mode csv   then   .import --skip 1 data/checkout_sessions.csv checkout_sessions
-- MySQL:       LOAD DATA LOCAL INFILE 'data/checkout_sessions.csv' INTO TABLE checkout_sessions
--              FIELDS TERMINATED BY ',' IGNORE 1 LINES;
