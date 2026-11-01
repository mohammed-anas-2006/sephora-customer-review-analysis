"""Week 2 - Step 1: data inventory and data-quality profiling of the six Kaggle CSV files.

Run from anywhere:  python week2/code/01_data_inventory.py
Reads  : data/*reviews_*.csv, data/product_info.csv  (originals; never modified)
Writes : week2/tables/*.csv  and  week2/results/w2_inventory.json
"""
import glob, json, os, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA, TAB, RES = ROOT / "data", ROOT / "week2" / "tables", ROOT / "week2" / "results"
TAB.mkdir(parents=True, exist_ok=True); RES.mkdir(parents=True, exist_ok=True)
rev_files = sorted(glob.glob(str(DATA / "*reviews_*.csv")))
if len(rev_files) != 5 or not (DATA / "product_info.csv").is_file():
    print(
        "Expected five review CSV files and data/product_info.csv. "
        "Download the source files before running the inventory.",
        file=sys.stderr,
    )
    raise SystemExit(2)
prod = pd.read_csv(DATA / "product_info.csv")
clean = lambda f: os.path.basename(f).split("_", 1)[1] if os.path.basename(f)[0].isdigit() else os.path.basename(f)
R = {}

# ------------------------------------------------------------------ 1. file inventory
inv, parts, hashes, miss, schemas = [], [], [], pd.Series(dtype="int64"), set()
TEXTS = ["review_text", "review_title"]
for f in rev_files:
    d = pd.read_csv(f, low_memory=False)
    schemas.add(tuple(d.columns))
    inv.append(dict(file=clean(f), size_mb=round(os.path.getsize(f) / 1e6, 1), rows=len(d), columns=d.shape[1], role="customer reviews"))
    hashes.append(pd.util.hash_pandas_object(d.drop(columns="Unnamed: 0"), index=False).to_numpy())
    miss = miss.add(d.isnull().sum(), fill_value=0)
    d["review_text_empty"] = d.review_text.fillna("").str.strip().eq("")
    parts.append(d.drop(columns=TEXTS + ["Unnamed: 0"]))
    del d
inv.append(dict(file="product_info.csv", size_mb=round(os.path.getsize(DATA / "product_info.csv") / 1e6, 1), rows=len(prod), columns=prod.shape[1], role="product catalogue"))
df = pd.concat(parts, ignore_index=True); del parts
N = len(df); R["N"] = N; R["same_schema_all_review_files"] = len(schemas) == 1
inv_df = pd.DataFrame(inv); inv_df.to_csv(TAB / "t01_file_inventory.csv", index=False)
R["inventory"] = inv; R["total_size_mb"] = round(float(inv_df.size_mb.sum()), 1)

# ------------------------------------------------------------------ 2. missing values
m = miss.drop("Unnamed: 0").astype(int)
mt = pd.DataFrame({"missing": m, "percent": (100 * m / N).round(2)}).sort_values("missing", ascending=False)
mt.to_csv(TAB / "t02_missing_reviews.csv"); R["missing_reviews"] = mt.to_dict("index")
pm = prod.isnull().sum(); pm = pd.DataFrame({"missing": pm, "percent": (100 * pm / len(prod)).round(2)}); pm = pm[pm.missing > 0].sort_values("missing", ascending=False)
pm.to_csv(TAB / "t03_missing_product_info.csv"); R["missing_product_info"] = pm.to_dict("index")
R["review_text_empty_strings"] = int(df.review_text_empty.sum()); R["review_text_missing"] = int(m["review_text"])

# ------------------------------------------------------------------ 3. uniqueness
R["exact_duplicate_rows_ex_counter"] = int(pd.Series(np.concatenate(hashes)).duplicated().sum())
R["authors"] = int(df.author_id.nunique())
R["author_product_extra_reviews"] = int(df.duplicated(subset=["author_id", "product_id"]).sum())
per_author = df.author_id.value_counts()
R["reviews_per_author"] = dict(median=float(per_author.median()), max=int(per_author.max()), authors_with_1=int((per_author == 1).sum()), authors_ge10=int((per_author >= 10).sum()), share_reviews_by_authors_ge10=round(float(per_author[per_author >= 10].sum() / N * 100), 2))
R["product_id_unique_in_catalogue"] = bool(prod.product_id.is_unique)

# ------------------------------------------------------------------ 4. validity
v = {}
v["rating_outside_1_5"] = int((~df.rating.isin([1, 2, 3, 4, 5])).sum())
v["is_recommended_values"] = {str(k): int(c) for k, c in df.is_recommended.value_counts(dropna=False).items()}
v["helpfulness_outside_0_1"] = int(((df.helpfulness < 0) | (df.helpfulness > 1)).sum())
v["negative_feedback_counts"] = int(((df.total_feedback_count < 0) | (df.total_neg_feedback_count < 0) | (df.total_pos_feedback_count < 0)).sum())
v["price_nonpositive_or_missing_reviews"] = int((~(df.price_usd > 0)).sum())
v["price_nonpositive_or_missing_catalogue"] = int((~(prod.price_usd > 0)).sum())
t = pd.to_datetime(df.submission_time, errors="coerce")
v["unparseable_dates"] = int(t.isna().sum()); v["date_min"], v["date_max"] = str(t.min().date()), str(t.max().date())
v["total_feedback_ne_pos_plus_neg"] = int((df.total_feedback_count != df.total_pos_feedback_count + df.total_neg_feedback_count).sum())
has = df.total_feedback_count > 0
calc = df.total_pos_feedback_count / df.total_feedback_count.where(has)
v["helpfulness_present_when_feedback_zero"] = int((~has & df.helpfulness.notna()).sum())
v["helpfulness_missing_when_feedback_positive"] = int((has & df.helpfulness.isna()).sum())
v["helpfulness_matches_pos_share_pct"] = round(float((np.abs(df.helpfulness[has] - calc[has]) < 0.01).mean() * 100), 2)
v["share_reviews_zero_feedback_pct"] = round(float((~has).mean() * 100), 2)
aid = df.author_id.astype(str); nn = ~aid.str.fullmatch(r"\d+")
v["author_id_non_numeric_rows"] = int(nn.sum()); v["author_id_non_numeric_distinct"] = int(aid[nn].nunique())
v["author_id_non_numeric_examples"] = sorted(aid[nn].value_counts().head(3).index.tolist()) + ["dummyUser"] if (aid == "dummyUser").any() else aid[nn].value_counts().head(3).index.tolist()
v["author_id_non_numeric_prefixes"] = aid[nn].str.replace(r"\d+$", "", regex=True).value_counts().to_dict()
R["validity"] = v

# ------------------------------------------------------------------ 5. consistency of labels and identifiers
c = {}
for col in ["skin_type", "skin_tone", "eye_color", "hair_color"]:
    c[col] = {k: int(x) for k, x in df[col].value_counts(dropna=True).items()}
low = df.eye_color.dropna().str.strip().str.lower()
c["eye_color_case_insensitive_n"] = int(low.nunique()); c["eye_color_raw_n"] = int(df.eye_color.nunique())
bn = df.brand_name.dropna()
c["brand_names_raw"] = int(bn.nunique()); c["brand_names_normalised_casefold"] = int(bn.str.strip().str.casefold().nunique())
pn = df.groupby("product_id").agg(n_names=("product_name", "nunique"), n_brands=("brand_name", "nunique"), n_prices=("price_usd", "nunique"))
c["products_with_multiple_names"] = int((pn.n_names > 1).sum()); c["products_with_multiple_brands"] = int((pn.n_brands > 1).sum())
c["products_with_multiple_prices_in_reviews"] = int((pn.n_prices > 1).sum())
c["product_names_shared_by_multiple_ids"] = int((df.groupby("product_name").product_id.nunique() > 1).sum())
pr = df.groupby("product_id").price_usd.first().rename("p_rev").to_frame().join(prod.set_index("product_id").price_usd.rename("p_cat"))
c["review_price_differs_from_catalogue_price"] = int(((pr.p_rev - pr.p_cat).abs() > 0.005).sum()); c["products_compared_price"] = int(len(pr))
R["consistency"] = c

# ------------------------------------------------------------------ 6. referential integrity and coverage
rp = pd.Series(df.product_id.unique())
R["review_products"] = int(len(rp)); R["review_products_not_in_catalogue"] = int((~rp.isin(prod.product_id)).sum())
R["catalogue_products"] = int(len(prod)); R["catalogue_products_without_reviews"] = int((~prod.product_id.isin(rp)).sum())
R["brands_in_reviews"] = int(df.brand_name.nunique()); R["brands_in_catalogue"] = int(prod.brand_name.nunique())
cat = prod.assign(reviewed=prod.product_id.isin(rp)).groupby("primary_category").agg(catalogue_products=("product_id", "size"), reviewed_products=("reviewed", "sum"))
rcat = df[["product_id"]].merge(prod[["product_id", "primary_category"]], on="product_id").primary_category.value_counts().rename("reviews")
cat = cat.join(rcat).fillna(0).astype(int); cat["share_of_reviews_pct"] = (100 * cat.reviews / N).round(2); cat["share_of_catalogue_pct"] = (100 * cat.catalogue_products / len(prod)).round(2)
cat.sort_values("catalogue_products", ascending=False).to_csv(TAB / "t04_category_coverage.csv"); R["category_coverage"] = cat.to_dict("index")
cnt = df.groupby("product_id").size()
R["reviews_per_product"] = {k: float(x) for k, x in cnt.describe(percentiles=[.1, .25, .5, .75, .9, .99]).round(1).items()}
R["products_lt_10_reviews"] = int((cnt < 10).sum()); R["products_ge_100_reviews"] = int((cnt >= 100).sum()); R["products_ge_1000_reviews"] = int((cnt >= 1000).sum())
R["top10_products_share_pct"] = round(float(cnt.nlargest(10).sum() / N * 100), 2)
bc = df.groupby("brand_name").size()
R["brands_ge_1000_reviews"] = int((bc >= 1000).sum()); R["top10_brands_share_pct"] = round(float(bc.nlargest(10).sum() / N * 100), 2)
R["largest_brand"] = [bc.idxmax(), int(bc.max())]
cnt.rename("reviews").to_csv(TAB / "t05_reviews_per_product.csv")

# completeness / accuracy check: review counts and mean ratings in the files vs the catalogue's own 'reviews' and 'rating' fields
pi = prod.set_index("product_id")[["reviews", "rating"]].rename(columns={"reviews": "listed_reviews", "rating": "listed_rating"})
chk = df.groupby("product_id").rating.agg(files_reviews="size", files_mean="mean").join(pi)
ok = chk.dropna(subset=["listed_reviews", "listed_rating"])
R["count_check"] = dict(products_compared=int(len(ok)), listed_total=int(ok.listed_reviews.sum()), files_total=int(ok.files_reviews.sum()),
    share_files_of_listed_pct=round(float(ok.files_reviews.sum() / ok.listed_reviews.sum() * 100), 2),
    products_files_exceed_listed=int((ok.files_reviews > ok.listed_reviews).sum()), products_files_equal_listed=int((ok.files_reviews == ok.listed_reviews).sum()),
    products_files_below_listed=int((ok.files_reviews < ok.listed_reviews).sum()), median_ratio_files_to_listed=round(float((ok.files_reviews / ok.listed_reviews).median()), 3),
    mean_abs_diff_rating=round(float((ok.files_mean - ok.listed_rating).abs().mean()), 3), median_abs_diff_rating=round(float((ok.files_mean - ok.listed_rating).abs().median()), 3),
    spearman_counts=round(float(ok[["files_reviews", "listed_reviews"]].corr(method="spearman").iloc[0, 1]), 4), products_without_listed_values=int(len(chk) - len(ok)))

# ------------------------------------------------------------------ 7. time coverage
df["year"] = t.dt.year; df["ym"] = t.dt.to_period("M")
yr = df.groupby("year").agg(reviews=("rating", "size"), mean_rating=("rating", "mean"), median_rating=("rating", "median"), rec_rate=("is_recommended", "mean"), rec_missing_share=("is_recommended", lambda s: s.isna().mean()))
yr.round(4).to_csv(TAB / "t06_by_year.csv"); R["by_year"] = {int(k): v_ for k, v_ in yr.round(4).to_dict("index").items()}
mo = df.groupby("ym").agg(reviews=("rating", "size"), mean_rating=("rating", "mean"), rec_rate=("is_recommended", "mean"))
mo.index = mo.index.astype(str); mo.round(4).to_csv(TAB / "t07_by_month.csv")
R["months_with_reviews"] = int(len(mo)); R["peak_month"] = [mo.reviews.idxmax(), int(mo.reviews.max())]
R["share_reviews_2020_onward_pct"] = round(float((df.year >= 2020).mean() * 100), 2)
R["share_reviews_before_2015_pct"] = round(float((df.year < 2015).mean() * 100), 2)

# ------------------------------------------------------------------ 8. rating / recommendation descriptive statistics
r = df.rating
R["rating_stats"] = dict(mean=float(r.mean()), median=float(r.median()), mode=int(r.mode().iloc[0]), sd=float(r.std()), skewness=float(r.skew()), min=int(r.min()), max=int(r.max()),
                         counts={int(k): int(x) for k, x in r.value_counts().sort_index().items()}, pct={int(k): round(float(x * 100), 2) for k, x in r.value_counts(normalize=True).sort_index().items()})
rec = df.is_recommended
xt = pd.crosstab(df.rating, rec.map({1.0: "recommended", 0.0: "not recommended"}).fillna("not recorded"))
xt.to_csv(TAB / "t08_rating_by_recommendation_status.csv"); R["rating_by_rec_status"] = {int(k): v_ for k, v_ in xt.to_dict("index").items()}
R["rec_missing_share_by_rating_pct"] = {int(k): round(float(x * 100), 2) for k, x in df.groupby("rating").is_recommended.apply(lambda s: s.isna().mean()).items()}
R["rec_counts"] = dict(recommended=int((rec == 1).sum()), not_recommended=int((rec == 0).sum()), missing=int(rec.isna().sum()))
R["rec_rate_among_recorded_pct"] = round(float((rec == 1).sum() / rec.notna().sum() * 100), 2)

open(RES / "w2_inventory.json", "w").write(json.dumps(R, indent=1, default=str).replace(": NaN", ": null"))  # valid JSON (NaN -> null)
print("done. rows:", N, "| exact duplicates:", R["exact_duplicate_rows_ex_counter"])
