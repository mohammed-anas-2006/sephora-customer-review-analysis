"""Sephora reviews - Week 1 exploratory analysis (full dataset).

Run from anywhere:  python code/analysis.py
Reads  : data/*reviews_*.csv and data/product_info.csv  (original Kaggle files, never modified)
Writes : code/results.json  (every number used in the report)
Text-based keyword themes are computed separately by code/themes_full.py (memory-friendly, chunked).
"""
import glob, json, os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "code" / "results.json"

files = sorted(glob.glob(str(DATA / "*reviews_*.csv")))
assert len(files) == 5, f"expected 5 review files in {DATA}, found {len(files)}"
prod = pd.read_csv(DATA / "product_info.csv")
NUM_COLS = ["author_id", "rating", "is_recommended", "helpfulness", "total_feedback_count",
            "submission_time", "skin_tone", "eye_color", "skin_type", "hair_color",
            "product_id", "product_name", "brand_name", "price_usd"]

R = {}
# ---------------------------------------------------------------- 1. files, duplicates, missing values
parts, hashes, miss, idx_all = [], [], pd.Series(dtype="int64"), []
R["files"] = {}
for f in files:
    name = os.path.basename(f).split("_", 1)[1] if os.path.basename(f)[0].isdigit() else os.path.basename(f)
    d = pd.read_csv(f, low_memory=False)
    R["files"][name] = dict(rows=len(d), cols=d.shape[1], idx_min=int(d["Unnamed: 0"].min()), idx_max=int(d["Unnamed: 0"].max()))
    idx_all.append(d["Unnamed: 0"].to_numpy())
    content = d.drop(columns="Unnamed: 0")               # row counter ignored
    hashes.append(pd.util.hash_pandas_object(content, index=False).to_numpy())
    miss = miss.add(d.isnull().sum(), fill_value=0)
    parts.append(d[NUM_COLS])                              # keep non-text columns only (memory)
    del d, content
df = pd.concat(parts, ignore_index=True); del parts
N = len(df)
R["total_rows"] = N
R["dup_full_excl_index"] = int(pd.Series(np.concatenate(hashes)).duplicated().sum())
R["dup_index_cross"] = int(pd.Series(np.concatenate(idx_all)).duplicated().sum())
R["missing"] = {k: int(v) for k, v in miss.drop("Unnamed: 0").sort_values(ascending=False).items()}
R["dtypes_note"] = "see notebook"
R["unique_products"] = int(df.product_id.nunique()); R["unique_brands"] = int(df.brand_name.nunique())
R["unique_authors"] = int(df.author_id.nunique())
R["prod_info_shape"] = list(prod.shape); R["prod_info_cols"] = list(prod.columns)
R["review_products_not_in_info"] = int((~pd.Series(df.product_id.unique()).isin(prod.product_id)).sum())
R["prod_dup_ids"] = int(prod.product_id.duplicated().sum())

# ---------------------------------------------------------------- 2. ratings and recommendation
R["rating_counts"] = {int(k): int(v) for k, v in df.rating.value_counts().sort_index().items()}
R["rating_mean"] = float(df.rating.mean())
rec = df.is_recommended
R["rec_counts"] = {"1.0": int((rec == 1).sum()), "0.0": int((rec == 0).sum()), "NaN": int(rec.isna().sum())}
R["rec_missing"] = int(rec.isna().sum())
g = df.groupby("rating").agg(n=("is_recommended", "size"), rec=("is_recommended", "sum"),
                             known=("is_recommended", "count"), rate=("is_recommended", "mean"))
R["rec_by_rating"] = {str(int(k)): dict(n=int(v.n), rec=int(v.rec), known=int(v.known), rate=float(v.rate)) for k, v in g.iterrows()}
k = df.dropna(subset=["is_recommended"])
chi = stats.chi2_contingency(pd.crosstab(k.rating, k.is_recommended))
R["chi2"] = [float(chi[0]), float(chi[1])]
R["spearman_rating_rec"] = float(k.rating.corr(k.is_recommended, method="spearman"))

# ---------------------------------------------------------------- 3. initial 1,000-row sample
first = [f for f in files if "reviews_0-250" in f][0]
s = pd.read_csv(first, nrows=1000, low_memory=False)
R["sample_rating"] = {int(a): int(b) for a, b in s.rating.value_counts().sort_index().items()}
sg = s.groupby("rating").agg(n=("is_recommended", "size"), rec=("is_recommended", "sum"), rate=("is_recommended", "mean"))
R["sample_rec"] = {str(int(a)): dict(n=int(r.n), rec=int(r.rec), rate=float(r.rate)) for a, r in sg.iterrows()}
R["sample_brands"] = {a: int(b) for a, b in s.brand_name.value_counts().items()}
R["sample_brand_mean"] = {a: round(float(b), 3) for a, b in s.groupby("brand_name").rating.mean().items()}
R["sample_missing"] = {a: int(b) for a, b in s.isnull().sum()[lambda x: x > 0].items()}
R["sample_products"] = int(s.product_id.nunique())

# ---------------------------------------------------------------- 4. brands and products
b = df.groupby("brand_name").agg(n=("rating", "size"), mean=("rating", "mean"), rec=("is_recommended", "mean"))
R["brand_top_n"] = b.sort_values("n", ascending=False).head(10).round(3).to_dict("index")
bb = b[b.n >= 1000].sort_values("mean")
R["brand_n1000"] = int(len(bb))
R["brand_lowest"] = bb.head(5).round(3).to_dict("index"); R["brand_highest"] = bb.tail(5).round(3).to_dict("index")
p = df.groupby(["product_id", "product_name", "brand_name"]).agg(n=("rating", "size"), mean=("rating", "mean"), rec=("is_recommended", "mean")).reset_index()
R["prod_n_median"] = float(p.n.median()); R["prod_n_max"] = int(p.n.max()); R["prod_ge100"] = int((p.n >= 100).sum())
pp = p[p.n >= 500].sort_values("mean")
R["prod_n500"] = int(len(pp))
R["prod_lowest"] = pp.head(5).round(3).to_dict("records"); R["prod_highest"] = pp.tail(5).round(3).to_dict("records")

# ---------------------------------------------------------------- 5. price (from product_info.csv) and customer attributes
R["price_desc"] = prod.price_usd.describe().round(2).to_dict()
dm = df[["product_id", "rating", "is_recommended"]].merge(prod[["product_id", "price_usd"]].rename(columns={"price_usd": "p2"}), on="product_id", how="left")
dm["pband"] = pd.cut(dm.p2, [0, 25, 50, 100, 1e9], labels=["<=25", "25-50", "50-100", ">100"])
R["price_band"] = dm.groupby("pband", observed=True).agg(n=("rating", "size"), mean=("rating", "mean"), rec=("is_recommended", "mean")).round(3).to_dict("index")
R["price_corr_review_level"] = float(dm[["p2", "rating"]].corr(method="spearman").iloc[0, 1])
for c in ["skin_type", "skin_tone", "eye_color", "hair_color"]:
    t = df.groupby(c).agg(n=("rating", "size"), mean=("rating", "mean")).round(3)
    R["by_" + c] = t.sort_values("n", ascending=False).head(8).to_dict("index")
t = pd.to_datetime(df.submission_time, errors="coerce")
R["date_min"], R["date_max"] = str(t.min().date()), str(t.max().date())
R["neg_total"] = int((df.rating <= 2).sum())

json.dump(R, open(OUT, "w"), indent=1, default=str)
print("saved", OUT, "| reviews:", N)
