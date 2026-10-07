"""Generate all visual assets for downthegroup episode 1. Only sourced numbers; nothing invented."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os

OUT = os.path.expanduser("~/workspace/youtube-video/assets")
os.makedirs(f"{OUT}/charts", exist_ok=True)
os.makedirs(f"{OUT}/cards", exist_ok=True)

NAVY, AMBER, WHITE, GREY = "#0a1628", "#f5a623", "#ffffff", "#8a94a6"
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": NAVY, "axes.facecolor": NAVY,
                     "text.color": WHITE, "axes.labelcolor": WHITE, "xtick.color": WHITE, "ytick.color": WHITE})

def save(fig, path):
    fig.savefig(path, dpi=100, bbox_inches="tight", facecolor=NAVY)
    plt.close(fig)
    print("wrote", path)

# 1. Russia's share of India's crude imports — sourced anchor points
fig, ax = plt.subplots(figsize=(12, 6.5))
labels = ["2021\n(pre-war)", "FY2026\n(full year)", "July 2026\n(single month)"]
vals = [2, 30.3, 51.1]
bars = ax.bar(labels, vals, color=[GREY, AMBER, "#e25822"], width=0.55)
ax.set_ylim(0, 60)
ax.set_ylabel("Share of India's crude imports (%)", fontsize=13)
ax.set_title("Russia's share of India's oil imports", fontsize=18, pad=16, color=WHITE, weight="bold")
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v + 1.2, f"{v}%", ha="center", fontsize=16, weight="bold",
            color=AMBER if v > 10 else WHITE)
ax.text(0.5, -0.18, "Sources: GTRI via Economic Times (FY2026, July 2026); ~2% pre-war widely reported",
        transform=ax.transAxes, ha="center", fontsize=9, color=GREY)
ax.spines[["top", "right"]].set_visible(False)
save(fig, f"{OUT}/charts/share_bar.png")

# 2. July 2026 supplier pie — GTRI figures
fig, ax = plt.subplots(figsize=(12, 6.5))
suppliers = ["Russia", "UAE", "Saudi Arabia", "Venezuela", "Brazil", "Oman", "USA", "Others"]
shares = [51.1, 10.8, 9.6, 6.3, 5.5, 5.3, 2.9, 8.5]
colors = ["#e25822", AMBER, "#c98a2d", GREY, "#6b7484", "#565e6e", "#434a58", "#2c3444"]
wedges, texts, autotexts = ax.pie(shares, labels=suppliers, autopct=lambda p: f"{p:.1f}%" if p > 5 else "",
                                  colors=colors, startangle=90, textprops={"fontsize": 12, "color": WHITE},
                                  wedgeprops={"edgecolor": NAVY, "linewidth": 2})
for t in autotexts:
    t.set_weight("bold"); t.set_color(NAVY if t.get_text().startswith("51") else WHITE)
ax.set_title("Who sold India oil in July 2026", fontsize=18, color=WHITE, weight="bold", pad=16)
fig.text(0.5, 0.02, "Source: GTRI via Economic Times", ha="center", fontsize=9, color=GREY)
save(fig, f"{OUT}/charts/suppliers_pie.png")

# 3. Discount spread — illustrative, clearly labeled, no invented values
fig, ax = plt.subplots(figsize=(12, 6.5))
x = np.linspace(0, 10, 200)
brent = 100 + 8 * np.sin(x * 0.8) + x * 1.2
urals = brent - (5 + 28 / (1 + np.exp(-(x - 3.5))) + 4 * np.sin(x))
ax.plot(x, brent, color=WHITE, lw=2.5, label="Global benchmark (Brent)")
ax.plot(x, urals, color=AMBER, lw=2.5, label="Russian crude to India")
ax.fill_between(x, urals, brent, where=(x > 3), color=AMBER, alpha=0.25)
ax.set_xlim(0, 10); ax.set_xticks([1, 4, 7, 9]); ax.set_xticklabels(["2021", "2022", "2024", "2026"])
ax.set_yticks([]); ax.set_ylabel("Price  →", fontsize=13)
ax.set_title("The discount gap after sanctions", fontsize=18, color=WHITE, weight="bold", pad=16)
ax.legend(frameon=False, fontsize=12, loc="upper left")
ax.annotate("sanctions hit", xy=(3.6, urals[72]), xytext=(2.2, brent[40] + 12),
            arrowprops={"arrowstyle": "->", "color": AMBER}, color=WHITE, fontsize=12)
fig.text(0.5, 0.02, "Illustrative — shape of the discount, not to scale. Reported low: ~$35/bbl.", ha="center", fontsize=9, color=GREY)
ax.spines[["top", "right", "left"]].set_visible(False)
save(fig, f"{OUT}/charts/discount_spread.png")

# 4. Section title cards (1920x1080)
def card(lines, fname, accent=AMBER):
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.axhline(0.5, xmin=0.08, xmax=0.92, color="#1c2a44", lw=2)
    for i, (txt, size, wt, col, y) in enumerate(lines):
        ax.text(0.5, y, txt, ha="center", va="center", fontsize=size, weight=wt, color=col,
                transform=ax.transAxes)
    ax.text(0.5, 0.06, "DOWNTHEGROUP", ha="center", fontsize=20, color=GREY, weight="bold",
            transform=ax.transAxes, alpha=0.7)
    fig.savefig(f"{OUT}/cards/{fname}", dpi=100, facecolor=NAVY)
    plt.close(fig); print("wrote", fname)

card([("PUNISHED: INDIA", 72, "bold", "#e25822", 0.62), ("SPARED: CHINA", 72, "bold", GREY, 0.42)], "hook.png")
card([("THE DISCOUNT", 88, "bold", AMBER, 0.55), ("why Russian oil got cheap", 34, "normal", WHITE, 0.42)], "beat_discount.png")
card([("THE $60 LOOPHOLE", 88, "bold", AMBER, 0.55), ("the door the West left open", 34, "normal", WHITE, 0.42)], "beat_loophole.png")
card([("THE THREAT", 88, "bold", AMBER, 0.55), ("25% tariffs, then the 100% law", 34, "normal", WHITE, 0.42)], "beat_threat.png")
card([("WHY INDIA WON'T STOP", 80, "bold", AMBER, 0.55), ("2 million barrels a day of reasons", 34, "normal", WHITE, 0.42)], "beat_why.png")
card([("WASHINGTON: LEVERAGE", 64, "bold", "#e25822", 0.60), ("DELHI: SURVIVAL", 64, "bold", AMBER, 0.42)], "payoff.png")
card([("DOWNTHEGROUP", 88, "bold", WHITE, 0.55), ("let's go deep — every week", 34, "normal", GREY, 0.42)], "endcard.png")

print("ALL ASSETS DONE")
