"""Week 2 - Step 2: preliminary statistics (with effect sizes / confidence intervals) and review-text profile.

Run after step 1:  python week2/code/02_stats_and_text_profile.py
Reads  : data/*reviews_*.csv
Writes : week2/tables/t09-t13*.csv and week2/results/w2_stats.json
"""
import glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]; DATA, TAB, RES = ROOT / "data", ROOT / "week2" / "tables", ROOT / "week2" / "results"
files = sorted(glob.glob(str(DATA / "*reviews_*.csv")))
if len(files) != 5:
    print(
        f"Expected five review CSV files in {DATA}; found {len(files)}. "
        "Download the source files before running the statistics step.",
        file=sys.stderr,
    )
    raise SystemExit(2)
TAB.mkdir(parents=True, exist_ok=True); RES.mkdir(parents=True, exist_ok=True)
USE = ["author_id", "rating", "is_recommended", "submission_time", "skin_type", "brand_name", "product_id", "review_text"]
parts, lens, rts = [], [], []
for f in files:
    d = pd.read_csv(f, usecols=USE, low_memory=False)
    txt = d.review_text.fillna("")
    lens.append(txt.str.split().str.len().to_numpy(dtype="int32")); rts.append(d.rating.to_numpy())
    parts.append(d.drop(columns="review_text"))
df = pd.concat(parts, ignore_index=True); del parts
words = np.concatenate(lens); rating = np.concatenate(rts); N = len(df)
df["year"] = pd.to_datetime(df.submission_time).dt.year
R = {}
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); a = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - a) / d, (c + a) / d

# ---------------- A. recommendation vs rating: all reviews with a decision vs 2018+ (when the field is recorded)
def rec_table(sub):
    g = sub.dropna(subset=["is_recommended"]).groupby("rating").is_recommended.agg(["size", "sum"])
    out = {}
    for k, r in g.iterrows():
        lo, hi = wilson(r["sum"], r["size"]); out[int(k)] = dict(n=int(r["size"]), rec=int(r["sum"]), rate=float(r["sum"] / r["size"]), ci_lo=float(lo), ci_hi=float(hi))
    k_ = sub.dropna(subset=["is_recommended"]); rho = float(k_.rating.corr(k_.is_recommended, method="spearman"))
    return out, rho, int(len(k_))
R["rec_all_recorded"], R["rho_all_recorded"], R["n_all_recorded"] = rec_table(df)
R["rec_2018_plus"], R["rho_2018_plus"], R["n_2018_plus"] = rec_table(df[df.year >= 2018])
pd.DataFrame({"all_recorded_rate_%": {k: round(v["rate"] * 100, 2) for k, v in R["rec_all_recorded"].items()}, "2018_plus_rate_%": {k: round(v["rate"] * 100, 2) for k, v in R["rec_2018_plus"].items()},
              "2018_plus_ci95_lo_%": {k: round(v["ci_lo"] * 100, 2) for k, v in R["rec_2018_plus"].items()}, "2018_plus_ci95_hi_%": {k: round(v["ci_hi"] * 100, 2) for k, v in R["rec_2018_plus"].items()}}).to_csv(TAB / "t09_recommendation_by_rating_sensitivity.csv")
k_ = df.dropna(subset=["is_recommended"]); ct = pd.crosstab(k_.rating, k_.is_recommended); chi = stats.chi2_contingency(ct)
R["chi2_rating_vs_rec"] = dict(chi2=float(chi[0]), dof=int(chi[2]), cramers_v=float(np.sqrt(chi[0] / (ct.values.sum() * (min(ct.shape) - 1)))))
# recommendation among reviews with a recorded decision, 2018+ only
sub = df[(df.year >= 2018)].dropna(subset=["is_recommended"]); R["rec_rate_2018_plus_overall"] = float(sub.is_recommended.mean())

# ---------------- B. rating over time
yr = df.groupby("year").rating.mean(); R["spearman_year_rating"] = float(df.year.corr(df.rating, method="spearman"))

# ---------------- C. brands: mean rating with 95% CI (top 10 by volume), Kruskal-Wallis over brands with >=1000 reviews
b = df.groupby("brand_name").rating.agg(["size", "mean", "std"]).sort_values("size", ascending=False)
top = b.head(10).copy(); top["ci95"] = 1.96 * top["std"] / np.sqrt(top["size"])
rr = df.groupby("brand_name").is_recommended.agg(["count", "sum"]).loc[top.index]
top["rec_rate"] = rr["sum"] / rr["count"]; top["rec_lo"], top["rec_hi"] = zip(*[wilson(s, c) for s, c in zip(rr["sum"], rr["count"])])
top.round(4).to_csv(TAB / "t10_top_brands_with_ci.csv"); R["top_brands_ci"] = top.round(4).to_dict("index")
big = b[b["size"] >= 1000].index; sub = df[df.brand_name.isin(big)]
groups = [g.rating.to_numpy() for _, g in sub.groupby("brand_name")]
H, p = stats.kruskal(*groups); n = sum(len(g) for g in groups); k = len(groups)
R["kruskal_brands"] = dict(groups=k, n=int(n), H=float(H), p=float(p), epsilon_squared=float(H / (n - 1)))
# customer attribute: skin type
st = df.dropna(subset=["skin_type"]); H2, p2 = stats.kruskal(*[g.rating.to_numpy() for _, g in st.groupby("skin_type")]); n2 = len(st)
R["kruskal_skin_type"] = dict(groups=int(st.skin_type.nunique()), n=int(n2), H=float(H2), p=float(p2), epsilon_squared=float(H2 / (n2 - 1)))
R["skin_type_means"] = {k_: round(float(v), 3) for k_, v in st.groupby("skin_type").rating.mean().items()}
# multiple-comparison note: Holm threshold for all pairwise brand tests
R["pairwise_brand_tests_if_all_compared"] = int(k * (k - 1) / 2)

# ---------------- D. review length
R["words"] = dict(mean=float(words.mean()), median=float(np.median(words)), p90=float(np.percentile(words, 90)), max=int(words.max()),
                  share_le_5_words_pct=float((words <= 5).mean() * 100), share_zero_words_pct=float((words == 0).mean() * 100))
L = pd.DataFrame({"rating": rating, "words": words}).groupby("rating").words.agg(["mean", "median", lambda s: s.quantile(.9)]); L.columns = ["mean", "median", "p90"]
L.round(1).to_csv(TAB / "t11_review_length_by_rating.csv"); R["length_by_rating"] = L.round(1).to_dict("index")
R["spearman_length_rating"] = float(stats.spearmanr(words, rating).statistic)
R["spearman_length_rating_note"] = "computed on all reviews with non-missing rating; zero-word texts are retained"
pd.DataFrame({"words": words}).describe(percentiles=[.5, .9, .99]).round(1).to_csv(TAB / "t12_review_length_summary.csv")
open(RES / "w2_stats.json", "w").write(json.dumps(R, indent=1, default=str).replace(": NaN", ": null"))
print(json.dumps({k_: R[k_] for k_ in ["rho_all_recorded", "rho_2018_plus", "n_2018_plus", "chi2_rating_vs_rec", "spearman_year_rating", "kruskal_brands", "kruskal_skin_type", "words", "spearman_length_rating"]}, indent=1))
