"""Week 2 - Step 4: draw the supporting figures from the saved results (run steps 1-3 first).

Run:  python week2/code/04_make_week2_figures.py   ->  week2/figures/w2_fig01 ... w2_fig09 (PNG)
"""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]; W2 = ROOT / "week2"; OUT = W2 / "figures"; OUT.mkdir(exist_ok=True)
I = json.load(open(W2 / "results" / "w2_inventory.json")); S = json.load(open(W2 / "results" / "w2_stats.json")); NLP = json.load(open(W2 / "results" / "w2_nlp_pilot.json"))
BLUE, RED, GREY, GREEN, AMBER = "#2E6F95", "#C8553D", "#7A8B99", "#3F8F6B", "#D9A441"
plt.rcParams.update({"font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False})
N = I["N"]

# Fig 1 - missing values by column
m = pd.DataFrame(I["missing_reviews"]).T; m = m[m.missing > 0].sort_values("percent")
f, a = plt.subplots(figsize=(7.5, 4)); a.barh(m.index, m.percent, color=BLUE)
for i, (k, r) in enumerate(m.iterrows()): a.text(r.percent + .6, i, f"{r.percent:.1f}%  ({int(r.missing):,})", va="center", fontsize=9)
a.set_xlim(0, 65); a.set_xlabel("Share of the 1,094,411 reviews with a missing value (%)"); a.set_title("Missing values by column (review files)")
plt.tight_layout(); plt.savefig(OUT / "w2_fig01_missing_values.png", dpi=200); plt.close()

# Fig 2 - reviews and mean rating by year; share with recommendation recorded
y = pd.DataFrame(I["by_year"]).T; y.index = y.index.astype(int)
f, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))
a.bar(y.index, y.reviews / 1000, color=BLUE); a.set_ylabel("Reviews (thousands)"); a.set_xlabel("Year of review (2023 = Jan-Mar only)"); a.set_title("(a) Reviews and mean rating by year")
a2 = a.twinx(); a2.plot(y.index, y.mean_rating, color=RED, marker="o"); a2.set_ylim(4.0, 4.6); a2.set_ylabel("Mean rating", color=RED); a2.spines["right"].set_visible(True)
b.bar(y.index, (1 - y.rec_missing_share) * 100, color=GREEN); b.set_ylim(0, 108); b.set_ylabel("Reviews with a recommendation value (%)"); b.set_xlabel("Year of review"); b.set_title("(b) Share with is_recommended recorded")
plt.tight_layout(); plt.savefig(OUT / "w2_fig02_time_coverage.png", dpi=200); plt.close()

# Fig 3 - recommendation status by rating (100% stacked)
x = pd.DataFrame(I["rating_by_rec_status"]).T[["recommended", "not recommended", "not recorded"]]; x.index = x.index.astype(int); xp = x.div(x.sum(axis=1), axis=0) * 100
f, a = plt.subplots(figsize=(8, 4.3)); left = np.zeros(5)
for col, c in zip(xp.columns, [BLUE, RED, GREY]):
    a.barh(xp.index, xp[col], left=left, color=c, label=col)
    for i, (v, l) in enumerate(zip(xp[col], left)):
        if v > 6: a.text(l + v / 2, xp.index[i], f"{v:.0f}%", ha="center", va="center", color="white", fontsize=9)
    left += xp[col].to_numpy()
a.set_yticks(range(1, 6)); a.set_xlabel("Share of reviews at that star rating (%)"); a.set_ylabel("Star rating"); a.set_title("Recommendation status by star rating (all 1,094,411 reviews)"); a.legend(loc="lower center", bbox_to_anchor=(.5, -.32), ncol=3, frameon=False)
plt.tight_layout(); plt.savefig(OUT / "w2_fig03_recommendation_status_by_rating.png", dpi=200); plt.close()

# Fig 4 - top brands with 95% CI
t = pd.DataFrame(S["top_brands_ci"]).T.iloc[::-1]
f, (a, b) = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
a.errorbar(t["mean"], range(len(t)), xerr=t["ci95"].astype(float), fmt="o", color=BLUE, capsize=3); a.set_yticks(range(len(t))); a.set_yticklabels([f"{i} (n={int(n):,})" for i, n in zip(t.index, t["size"])], fontsize=9)
a.set_xlabel("Mean star rating (95% CI)"); a.set_title("(a) Mean rating")
b.errorbar(t["rec_rate"] * 100, range(len(t)), xerr=[(t["rec_rate"] - t["rec_lo"]) * 100, (t["rec_hi"] - t["rec_rate"]) * 100], fmt="s", color=GREEN, capsize=3); b.set_xlabel("Recommendation rate (%), 95% Wilson CI"); b.set_title("(b) Recommendation rate (recorded decisions)")
plt.tight_layout(); plt.savefig(OUT / "w2_fig04_top_brands_confidence_intervals.png", dpi=200); plt.close()

# Fig 5 - reviews per product
c = pd.read_csv(W2 / "tables" / "t05_reviews_per_product.csv").reviews
f, a = plt.subplots(figsize=(8, 4.2)); a.hist(c, bins=np.logspace(0, np.log10(c.max()), 40), color=BLUE); a.set_xscale("log")
a.axvline(c.median(), color=RED, ls="--"); a.text(c.median() * 1.1, a.get_ylim()[1] * .9, f"median = {c.median():.0f}", color=RED)
a.set_xlabel("Reviews per product (log scale)"); a.set_ylabel("Number of products"); a.set_title(f"Reviews per product ({len(c):,} products; {int((c < 10).sum())} have fewer than 10)")
plt.tight_layout(); plt.savefig(OUT / "w2_fig05_reviews_per_product.png", dpi=200); plt.close()

# Fig 6 - review length by rating
L = pd.DataFrame(S["length_by_rating"]).T; L.index = L.index.astype(int)
f, a = plt.subplots(figsize=(7, 4)); w = .38; a.bar(L.index - w / 2, L["mean"], w, color=BLUE, label="mean"); a.bar(L.index + w / 2, L["median"], w, color=AMBER, label="median")
for i in L.index: a.text(i - w / 2, L.loc[i, "mean"] + 1, f"{L.loc[i, 'mean']:.0f}", ha="center", fontsize=9); a.text(i + w / 2, L.loc[i, "median"] + 1, f"{L.loc[i, 'median']:.0f}", ha="center", fontsize=9)
a.set_xlabel("Star rating"); a.set_ylabel("Words per review"); a.set_title("Review length by star rating"); a.legend(frameon=False); plt.tight_layout(); plt.savefig(OUT / "w2_fig06_review_length_by_rating.png", dpi=200); plt.close()

# Fig 7 - pilot metrics
names = [("baseline_majority", "Majority-class\nbaseline"), ("vader", "VADER\n(lexicon)"), ("tfidf_nb", "TF-IDF +\nNaive Bayes"), ("tfidf_logreg", "TF-IDF +\nLogistic Reg.")]
f, a = plt.subplots(figsize=(8, 4.2)); x = np.arange(4); w = .38
acc = [NLP[k]["accuracy"] for k, _ in names]; mf = [NLP[k]["macro_f1"] for k, _ in names]
a.bar(x - w / 2, acc, w, color=GREY, label="Accuracy"); a.bar(x + w / 2, mf, w, color=BLUE, label="Macro-F1")
for i in range(4): a.text(i - w / 2, acc[i] + .01, f"{acc[i]:.3f}", ha="center", fontsize=9); a.text(i + w / 2, mf[i] + .01, f"{mf[i]:.3f}", ha="center", fontsize=9)
a.set_xticks(x); a.set_xticklabels([n for _, n in names]); a.set_ylim(0, 1.05); a.set_title(f"Pilot: 3-class weak-label sentiment (test n = {NLP['test_n']:,})"); a.legend(frameon=False, loc="upper left", ncol=2)
plt.tight_layout(); plt.savefig(OUT / "w2_fig07_nlp_pilot_metrics.png", dpi=200); plt.close()

# Fig 8 - confusion matrices (row-normalised)
f, axs = plt.subplots(1, 2, figsize=(9.5, 4)); labs = ["neg", "neu", "pos"]
for a, (k, ttl) in zip(axs, [("vader", "VADER"), ("tfidf_logreg", "TF-IDF + Logistic Regression")]):
    cm = np.array(NLP[k]["confusion"], float); cn = cm / cm.sum(axis=1, keepdims=True); im = a.imshow(cn, cmap="Blues", vmin=0, vmax=1)
    for i in range(3):
        for j in range(3): a.text(j, i, f"{cn[i, j]*100:.0f}%\n({int(cm[i, j]):,})", ha="center", va="center", color="white" if cn[i, j] > .5 else "black", fontsize=8.5)
    a.set_xticks(range(3)); a.set_yticks(range(3)); a.set_xticklabels(["pred " + l for l in labs]); a.set_yticklabels(["true " + l for l in labs]); a.set_title(ttl)
plt.suptitle("Confusion matrices against star-derived weak labels (row %)", y=1.02); plt.tight_layout(); plt.savefig(OUT / "w2_fig08_nlp_pilot_confusion.png", dpi=200, bbox_inches="tight"); plt.close()

# Fig 9 - category coverage
cc = pd.read_csv(W2 / "tables" / "t04_category_coverage.csv").set_index("primary_category").iloc[::-1]
f, a = plt.subplots(figsize=(8, 4.3)); a.barh(cc.index, cc.catalogue_products, color=GREY, label="Products in product_info.csv"); a.barh(cc.index, cc.reviewed_products, color=BLUE, label="Products with reviews in the review files")
for i, (n, r) in enumerate(zip(cc.catalogue_products, cc.reviewed_products)): a.text(n + 20, i, f"{n:,}" + (f"  ({r:,} reviewed)" if r else "  (0 reviewed)"), va="center", fontsize=9)
a.set_xlim(0, 3600); a.set_xlabel("Number of products"); a.set_title("Catalogue coverage by primary category"); a.legend(frameon=False, loc="lower right")
plt.tight_layout(); plt.savefig(OUT / "w2_fig09_category_coverage.png", dpi=200); plt.close()
print("figures saved:", sorted(p.name for p in OUT.glob("*.png")))
