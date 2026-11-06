"""
Generates a SIMULATED checkout-session dataset for the case study.

Nothing here comes from a real company. The pass-rates below are assumptions
chosen to look like typical e-commerce funnels (published benchmarks put
average cart abandonment at roughly 70%). Change the numbers, re-run, and
every downstream file (SQL, Excel, charts) can be rebuilt from the new CSV.

Usage:  python scripts/generate_dataset.py
Output: data/checkout_sessions.csv
"""
import numpy as np
import pandas as pd

SEED = 2026
N_SESSIONS = 25_000          # sessions that reached the cart page
START, END = "2026-07-01", "2026-09-30"

rng = np.random.default_rng(SEED)

STEPS = {
    1: "Cart",
    2: "Login / Create Account",
    3: "Shipping Address",
    4: "Delivery Options",
    5: "Payment Details",
    6: "Gateway Authorisation",
    7: "Order Confirmed",
}

# ---------- session attributes ----------
dates = pd.date_range(START, END, freq="D")
# slightly heavier traffic at month end / weekends
day_weights = np.array([1.15 if d.dayofweek >= 5 else 1.0 for d in dates])
day_weights /= day_weights.sum()
session_date = rng.choice(dates, size=N_SESSIONS, p=day_weights)

device = rng.choice(["Mobile", "Desktop", "Tablet"], N_SESSIONS, p=[0.62, 0.31, 0.07])
source = rng.choice(
    ["Organic Search", "Paid Search", "Social", "Email", "Direct"],
    N_SESSIONS, p=[0.30, 0.25, 0.17, 0.13, 0.15],
)
customer_type = rng.choice(["New", "Returning"], N_SESSIONS, p=[0.64, 0.36])

cart_value = np.round(np.clip(rng.lognormal(mean=4.25, sigma=0.55, size=N_SESSIONS), 9, 600), 2)
items = np.clip(np.round(cart_value / rng.uniform(22, 45, N_SESSIONS)), 1, 12).astype(int)

FREE_SHIP_THRESHOLD = 75.0
shipping_cost = np.where(cart_value >= FREE_SHIP_THRESHOLD, 0.0, 6.99)

pay_load = np.round(np.clip(rng.normal(3.1, 1.3, N_SESSIONS), 0.8, 12), 1)
pay_load = np.where(device == "Mobile", pay_load + 0.9, pay_load)
pay_load = np.round(pay_load, 1)

payment_method = rng.choice(["Credit/Debit Card", "PayPal"], N_SESSIONS, p=[0.78, 0.22])


# ---------- pass probabilities per step ----------
def clip(p):
    return np.clip(p, 0.05, 0.97)


p = {}
# 1 -> 2 : cart to checkout
p[1] = 0.80 - 0.04 * (device == "Mobile") + 0.05 * (source == "Email") - 0.05 * (source == "Social")
# 2 -> 3 : forced account creation hurts new customers
p[2] = np.where(customer_type == "Returning", 0.90, 0.68) - 0.03 * (device == "Mobile")
# 3 -> 4 : long address form, worse on small screens
p[3] = np.select([device == "Desktop", device == "Mobile"], [0.93, 0.84], default=0.88)
# 4 -> 5 : shipping cost reveal
p[4] = np.where(shipping_cost > 0, 0.76, 0.91)
# 5 -> 6 : payment form (slow page + typing card number on a phone)
p[5] = np.select([device == "Desktop", device == "Mobile"], [0.86, 0.75], default=0.80) - 0.10 * (pay_load > 4.5)
# 6 -> 7 : 3-D Secure / redirect / declines
p[6] = (np.select([device == "Desktop", device == "Mobile"], [0.75, 0.62], default=0.68)
        + 0.05 * (payment_method == "PayPal") - 0.04 * (pay_load > 4.5))

last_step = np.ones(N_SESSIONS, dtype=int)
alive = np.ones(N_SESSIONS, dtype=bool)
for s in range(1, 7):
    passed = rng.random(N_SESSIONS) < clip(p[s])
    advance = alive & passed
    last_step = np.where(advance, s + 1, last_step)
    alive = advance

converted = (last_step == 7).astype(int)

# ---------- system-captured exit tags (only for sessions that dropped) ----------
EXIT = {
    1: (["Left after viewing cart", "Price comparison", "Idle timeout"], [0.55, 0.25, 0.20]),
    2: (["Account creation abandoned", "Password / login issue", "Left at login wall"], [0.50, 0.20, 0.30]),
    3: (["Address form abandoned", "Validation error", "Left after form load"], [0.55, 0.20, 0.25]),
    4: (["Shipping cost too high", "Delivery time too long", "No preferred carrier"], [0.62, 0.23, 0.15]),
    5: (["Payment form abandoned", "Page load too slow", "Wanted wallet option"], [0.45, 0.25, 0.30]),
    6: (["3-D Secure timeout/fail", "Card declined", "Redirect abandoned", "Gateway error/timeout", "Session expired"],
        [0.34, 0.22, 0.18, 0.16, 0.10]),
}
exit_tag = np.array([""] * N_SESSIONS, dtype=object)
for s, (labels, probs) in EXIT.items():
    idx = np.where(last_step == s)[0]
    exit_tag[idx] = rng.choice(labels, size=len(idx), p=probs)
exit_tag = np.where(converted == 1, "", exit_tag)

payment_attempted = np.where(last_step >= 5, payment_method, "")
gateway_error = np.where(np.isin(exit_tag, ["Gateway error/timeout", "Session expired"]), 1, 0)

df = pd.DataFrame({
    "session_id": [f"S{100000 + i}" for i in range(N_SESSIONS)],
    "session_date": pd.to_datetime(session_date).strftime("%Y-%m-%d"),
    "device_type": device,
    "traffic_source": source,
    "customer_type": customer_type,
    "items_in_cart": items,
    "cart_value_usd": cart_value,
    "shipping_cost_usd": shipping_cost,
    "payment_page_load_sec": pay_load,
    "last_step_reached": last_step,
    "last_step_name": [STEPS[s] for s in last_step],
    "payment_method_attempted": payment_attempted,
    "exit_tag": exit_tag,
    "gateway_error_flag": gateway_error,
    "converted": converted,
}).sort_values(["session_date", "session_id"]).reset_index(drop=True)

df.to_csv("data/checkout_sessions.csv", index=False)
print(f"rows: {len(df):,} | conversion: {df.converted.mean():.1%}")
