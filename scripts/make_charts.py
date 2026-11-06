"""Builds the PNG charts used in the README and the BRD from data/checkout_sessions.csv"""
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
NAVY, RED, GREY, TEAL = "#1F3A5F", "#C8483B", "#A9B4C2", "#2A9D8F"

d = pd.read_csv("data/checkout_sessions.csv")
names = ["Cart", "Login /\nCreate Account", "Shipping\nAddress", "Delivery\nOptions",
         "Payment\nDetails", "Gateway\nAuthorisation", "Order\nConfirmed"]
reached = [(d.last_step_reached >= s).sum() for s in range(1, 8)]

# 1. funnel
fig, ax = plt.subplots(figsize=(10, 5.2))
colors = [NAVY] * 7
colors[4] = colors[5] = RED
bars = ax.bar(names, reached, color=colors, width=0.62)
for i, (b, v) in enumerate(zip(bars, reached)):
    ax.text(b.get_x() + b.get_width() / 2, v + 400, f"{v:,}", ha="center", fontsize=9, fontweight="bold")
    if i > 0:
        ax.text(b.get_x() + b.get_width() / 2, v / 2, f"{v / reached[i-1]:.0%}\nof prev.", ha="center",
                color="white", fontsize=8.5)
ax.set_ylabel("Sessions reaching step")
ax.set_title("AS-IS checkout funnel (25,000 simulated cart sessions)", loc="left", fontsize=13, fontweight="bold")
ax.set_ylim(0, 28500)
plt.tight_layout(); plt.savefig("images/01_funnel.png", dpi=160); plt.close()

# 2. where sessions are lost (share of all exits)
lost = [reached[i] - reached[i + 1] for i in range(6)]
labels = ["Cart →\nLogin", "Login →\nShipping", "Shipping →\nDelivery", "Delivery →\nPayment", "Payment →\nGateway", "Gateway →\nConfirm"]
fig, ax = plt.subplots(figsize=(10, 4.8))
cols = [GREY, GREY, GREY, GREY, RED, RED]
bars = ax.bar(labels, lost, color=cols, width=0.6)
for b, v in zip(bars, lost):
    ax.text(b.get_x() + b.get_width() / 2, v + 60, f"{v:,}\n({v / sum(lost):.0%})", ha="center", fontsize=9)
ax.set_ylim(0, 6800); ax.set_ylabel("Sessions lost")
ax.set_title("Sessions lost per step (payment steps highlighted)", loc="left", fontsize=13, fontweight="bold")
plt.tight_layout(); plt.savefig("images/02_loss_by_step.png", dpi=160); plt.close()

# 3. device conversion
g = d.groupby("device_type").apply(lambda x: pd.Series({
    "overall": x.converted.mean() * 100,
    "gateway": (x.last_step_reached == 7).sum() / max((x.last_step_reached >= 6).sum(), 1) * 100})).loc[["Desktop", "Tablet", "Mobile"]]
fig, ax = plt.subplots(figsize=(8, 4.6))
x = range(3); w = 0.36
b1 = ax.bar([i - w / 2 for i in x], g["overall"], w, color=NAVY, label="Cart → order")
b2 = ax.bar([i + w / 2 for i in x], g["gateway"], w, color=RED, label="Gateway pass rate")
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1, f"{b.get_height():.0f}%", ha="center", fontsize=9)
ax.set_xticks(list(x)); ax.set_xticklabels(g.index); ax.set_ylim(0, 95); ax.legend(frameon=False)
ax.set_title("Mobile converts far worse than desktop", loc="left", fontsize=13, fontweight="bold")
plt.tight_layout(); plt.savefig("images/03_device.png", dpi=160); plt.close()

# 4. gateway exit reasons
r = d[(d.last_step_reached == 6) & (d.converted == 0)].exit_tag.value_counts()
fig, ax = plt.subplots(figsize=(8.5, 4.2))
ax.barh(r.index[::-1], r.values[::-1], color=[GREY, GREY, GREY, GREY, RED])
for i, v in enumerate(r.values[::-1]):
    ax.text(v + 10, i, f"{v:,} ({v / r.sum():.0%})", va="center", fontsize=9)
ax.set_xlim(0, r.max() * 1.25)
ax.set_title("Why sessions exit at gateway authorisation", loc="left", fontsize=13, fontweight="bold")
plt.tight_layout(); plt.savefig("images/04_gateway_reasons.png", dpi=160); plt.close()
print("charts done")
