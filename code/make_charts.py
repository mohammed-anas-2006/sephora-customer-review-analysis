"""Draw all seven report figures from code/results.json (run analysis.py and themes_full.py first).

Run:  python code/make_charts.py      ->  charts/fig1 ... fig7 (PNG)
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
R = json.load(open(ROOT / "code" / "results.json"))
OUT = ROOT / "charts"; OUT.mkdir(exist_ok=True)
BLUE, RED, GREY = "#2E6F95", "#C8553D", "#7A8B99"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
N = R["total_rows"]; rc = {int(k): v for k, v in R["rating_counts"].items()}
rb = {int(k): v["rate"] * 100 for k, v in R["rec_by_rating"].items()}
sr = {int(k): v["rate"] * 100 for k, v in R["sample_rec"].items()}
sc = {int(k): v for k, v in R["sample_rating"].items()}

# Fig 1 - initial 1,000-review sample, rating counts
f, a = plt.subplots(figsize=(8, 5)); a.bar(list(sc), list(sc.values()), color=BLUE)
for x, v in sc.items(): a.text(x, v + 8, str(v), ha="center")
a.set_title("Distribution of Customer Star Ratings (initial 1,000-review sample)"); a.set_xlabel("Customer star rating"); a.set_ylabel("Number of reviews")
plt.tight_layout(); plt.savefig(OUT / "fig1_rating_distribution_sample.png", dpi=200); plt.close()

# Fig 2 - initial sample, recommendation rate by rating
f, a = plt.subplots(figsize=(8.5, 5)); a.bar(list(sr), list(sr.values()), color=BLUE)
for x, v in sr.items(): a.text(x, v + 1.5, f"{v:.1f}%", ha="center")
a.set_ylim(0, 112); a.set_title("Recommendation Rate by Customer Star Rating (initial 1,000-review sample)", fontsize=12)
a.set_xlabel("Customer star rating"); a.set_ylabel("Recommendation rate (%)")
plt.tight_layout(); plt.savefig(OUT / "fig2_recommendation_rate_sample.png", dpi=200); plt.close()

# Fig 3 - full dataset rating distribution
f, a = plt.subplots(figsize=(8, 4.8)); a.bar(list(rc), [v / 1000 for v in rc.values()], color=BLUE)
for x, v in rc.items(): a.text(x, v / 1000 + 10, f"{v:,}\n({100 * v / N:.1f}%)", ha="center", fontsize=10)
a.set_ylim(0, 820); a.set_title(f"Distribution of Customer Star Ratings (all {N:,} reviews)")
a.set_xlabel("Customer star rating"); a.set_ylabel("Number of reviews (thousands)")
plt.tight_layout(); plt.savefig(OUT / "fig3_rating_distribution_full.png", dpi=200); plt.close()

# Fig 4 - recommendation rate, sample vs full
f, a = plt.subplots(figsize=(8.5, 4.8)); x = np.arange(1, 6); w = .38
a.bar(x - w / 2, [sr[i] for i in x], w, color=GREY, label="Initial 1,000-review sample")
a.bar(x + w / 2, [rb[i] for i in x], w, color=BLUE, label="Full dataset (reviews with a recommendation value)")
for i in x:
    a.text(i - w / 2, sr[i] + 1.5, f"{sr[i]:.1f}%", ha="center", fontsize=9); a.text(i + w / 2, rb[i] + 1.5, f"{rb[i]:.1f}%", ha="center", fontsize=9)
a.set_ylim(0, 115); a.set_xlabel("Customer star rating"); a.set_ylabel("Recommendation rate (%)")
a.set_title("Recommendation Rate by Customer Star Rating"); a.legend(loc="upper left", frameon=False, fontsize=9)
plt.tight_layout(); plt.savefig(OUT / "fig4_recommendation_rate_full_vs_sample.png", dpi=200); plt.close()

# Fig 5 - recommended / not recommended / missing
rec = R["rec_counts"]; vals = [rec["1.0"], rec["0.0"], rec["NaN"]]
f, a = plt.subplots(figsize=(7.5, 4.5)); a.bar(["Recommended", "Not recommended", "Not recorded (missing)"], [v / 1000 for v in vals], color=[BLUE, RED, GREY])
for i, v in enumerate(vals): a.text(i, v / 1000 + 12, f"{v:,}\n({100 * v / N:.1f}%)", ha="center", fontsize=10)
a.set_ylim(0, 900); a.set_ylabel("Number of reviews (thousands)"); a.set_title("Recommended vs Non-Recommended Reviews")
plt.tight_layout(); plt.savefig(OUT / "fig5_recommended_vs_not.png", dpi=200); plt.close()

# Fig 6 - ten brands with most reviews
bt = R["brand_top_n"]; names = list(bt)[::-1]
f, a = plt.subplots(figsize=(8.5, 5)); a.barh(names, [bt[n]["mean"] for n in names], color=BLUE)
for i, n in enumerate(names): a.text(bt[n]["mean"] + .01, i, f"{bt[n]['mean']:.2f}  (n={bt[n]['n']:,})", va="center", fontsize=9)
a.set_xlim(3.5, 4.75); a.set_xlabel("Average star rating (axis starts at 3.5)"); a.set_title("Average Rating of the 10 Brands with Most Reviews")
plt.tight_layout(); plt.savefig(OUT / "fig6_top_brands.png", dpi=200); plt.close()

# Fig 7 - keyword themes
tn = {k: v[1] for k, v in R["themes_neg"].items()}; tp = R["themes_pos_pct"]
ks = sorted(tn, key=lambda k: tn[k]); y = np.arange(len(ks)); h = .38
f, a = plt.subplots(figsize=(8.5, 5))
a.barh(y + h / 2, [tn[k] for k in ks], h, color=RED, label=f"1-2 star reviews (n={R['neg_n']:,})")
a.barh(y - h / 2, [tp[k] for k in ks], h, color=GREY, label=f"5-star reviews (all, n={R['five_star_text_n']:,})")
a.set_yticks(y); a.set_yticklabels(ks); a.set_xlabel("% of reviews mentioning the theme (keyword matching)")
a.set_title("Keyword Themes: Low-Rated vs 5-Star Reviews"); a.legend(frameon=False, fontsize=9, loc="lower right")
plt.tight_layout(); plt.savefig(OUT / "fig7_complaint_themes.png", dpi=200); plt.close()
print("charts saved to", OUT)
