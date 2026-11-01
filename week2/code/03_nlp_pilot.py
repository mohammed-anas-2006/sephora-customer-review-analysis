"""Week 2 - Step 3: small, clearly-labelled PILOT of sentiment classification (weak labels from star ratings).

This is a feasibility pilot on a random sample, NOT a final model. Labels are weak: 1-2 stars = negative, 3 = neutral, 4-5 = positive.
Run:  python week2/code/03_nlp_pilot.py        (needs: pip install vaderSentiment scikit-learn)
Reads: data/*reviews_*.csv     Writes: week2/tables/t13-t16*.csv, week2/results/w2_nlp_pilot.json
"""
import glob, json, re, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; DATA, TAB, RES = ROOT / "data", ROOT / "week2" / "tables", ROOT / "week2" / "results"
review_files = sorted(glob.glob(str(DATA / "*reviews_*.csv")))
if len(review_files) != 5:
    raise SystemExit(
        f"Expected five review CSV files in {DATA}; found {len(review_files)}. "
        "Download the source files before running the NLP pilot."
    )
TAB.mkdir(parents=True, exist_ok=True); RES.mkdir(parents=True, exist_ok=True)
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit, GroupKFold
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

SEED, FRAC = 42, 100_000 / 1_094_411
LAB = {1: "negative", 2: "negative", 3: "neutral", 4: "positive", 5: "positive"}; ORDER = ["negative", "neutral", "positive"]
parts = []
for i, f in enumerate(review_files):
    for j, ch in enumerate(pd.read_csv(f, usecols=["author_id", "rating", "review_text"], chunksize=100_000)):
        ch = ch.dropna(subset=["review_text"]); parts.append(ch.sample(frac=FRAC, random_state=SEED + 100 * i + j))
if not parts:
    raise SystemExit("No review rows could be read for the NLP pilot.")
S = pd.concat(parts, ignore_index=True); S["author_id"] = S.author_id.astype(str); S["review_text"] = S.review_text.str.strip(); S = S[S.review_text.str.len() > 0].reset_index(drop=True)
if S.empty:
    raise SystemExit("No non-empty review text was found; the NLP pilot was not run.")
S["label"] = S.rating.map(LAB); R = {"sample_n": int(len(S)), "label_share_pct": {k: round(float(v * 100), 2) for k, v in S.label.value_counts(normalize=True).items()}}
# author-grouped split (no author appears in both train and test)
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED); tr, te = next(gss.split(S, groups=S.author_id))
Xtr, Xte, ytr, yte = S.review_text.iloc[tr], S.review_text.iloc[te], S.label.iloc[tr], S.label.iloc[te]
R["train_n"], R["test_n"] = int(len(tr)), int(len(te)); R["author_overlap_train_test"] = int(len(set(S.author_id.iloc[tr]) & set(S.author_id.iloc[te])))
R["test_label_share_pct"] = {k: round(float(v * 100), 2) for k, v in yte.value_counts(normalize=True).items()}

def evaluate(name, pred):
    rep = classification_report(yte, pred, labels=ORDER, output_dict=True, zero_division=0)
    cm = confusion_matrix(yte, pred, labels=ORDER)
    R[name] = dict(accuracy=float(accuracy_score(yte, pred)), macro_f1=float(f1_score(yte, pred, average="macro", labels=ORDER)),
                   per_class={c: {m: float(rep[c][m]) for m in ["precision", "recall", "f1-score", "support"]} for c in ORDER}, confusion=cm.tolist())
    pd.DataFrame(cm, index=[f"true_{c}" for c in ORDER], columns=[f"pred_{c}" for c in ORDER]).to_csv(TAB / f"t14_confusion_{name}.csv")

# baseline: always predict the majority class
evaluate("baseline_majority", np.array([yte.value_counts().idxmax()] * len(yte)))
# 1) VADER (lexicon, no training); standard +/-0.05 compound thresholds
t0 = time.time(); sia = SentimentIntensityAnalyzer(); comp = np.array([sia.polarity_scores(t)["compound"] for t in Xte])
vpred = np.where(comp >= 0.05, "positive", np.where(comp <= -0.05, "negative", "neutral")); evaluate("vader", vpred); R["vader_seconds"] = round(time.time() - t0, 1)
from scipy.stats import spearmanr
R["vader_spearman_with_rating"] = float(spearmanr(comp, S.rating.iloc[te])[0])
# 2) TF-IDF + logistic regression (class_weight=balanced); negations kept (no stop-word removal)
vec = TfidfVectorizer(ngram_range=(1, 2), min_df=5, max_features=50_000, sublinear_tf=True, strip_accents="unicode")
t0 = time.time(); A = vec.fit_transform(Xtr); B = vec.transform(Xte)
lr = LogisticRegression(max_iter=300, C=2.0, class_weight="balanced"); lr.fit(A, ytr); evaluate("tfidf_logreg", lr.predict(B)); R["logreg_seconds"] = round(time.time() - t0, 1)
# 3) TF-IDF + multinomial naive Bayes
nb = MultinomialNB(alpha=0.1); nb.fit(A, ytr); evaluate("tfidf_nb", nb.predict(B))

# Compact metrics table used by the report and for quick result comparisons.
metrics_rows = []
for method in ["baseline_majority", "vader", "tfidf_nb", "tfidf_logreg"]:
    result = R[method]
    row = {"method": method, "accuracy": result["accuracy"], "macro_f1": result["macro_f1"]}
    for class_name in ORDER:
        for metric in ["precision", "recall", "f1-score"]:
            row[f"{class_name}_{metric.replace('-', '_')}"] = result["per_class"][class_name][metric]
    metrics_rows.append(row)
pd.DataFrame(metrics_rows).to_csv(TAB / "t13_pilot_metrics.csv", index=False)

# 3-fold author-grouped cross-validation on the training part for logistic regression (macro-F1)
cv = []
for a, b in GroupKFold(n_splits=3).split(Xtr, groups=S.author_id.iloc[tr]):
    v2 = TfidfVectorizer(ngram_range=(1, 2), min_df=5, max_features=50_000, sublinear_tf=True, strip_accents="unicode"); Aa = v2.fit_transform(Xtr.iloc[a]); Bb = v2.transform(Xtr.iloc[b])
    m2 = LogisticRegression(max_iter=300, C=2.0, class_weight="balanced").fit(Aa, ytr.iloc[a]); cv.append(f1_score(ytr.iloc[b], m2.predict(Bb), average="macro"))
R["logreg_cv_macro_f1"] = dict(folds=[round(float(x), 4) for x in cv], mean=float(np.mean(cv)), sd=float(np.std(cv)))
# most informative n-grams per class (logistic-regression coefficients)
names = np.array(vec.get_feature_names_out()); terms = {}
for i, c in enumerate(lr.classes_): terms[c] = names[np.argsort(lr.coef_[i])[::-1][:25]].tolist()
R["top_terms"] = terms; pd.DataFrame(terms).to_csv(TAB / "t15_top_ngrams_by_class.csv", index=False)
# weak-label disagreement examples (short excerpts) between star rating and VADER
Te = S.iloc[te].assign(vader=comp); trunc = lambda s, n=28: " ".join(s.split()[:n]) + (" ..." if len(s.split()) > n else "")
neg_hi = Te[(Te.rating <= 2) & (Te.vader >= 0.8) & (Te.review_text.str.split().str.len() <= 40)]
pos_lo = Te[(Te.rating == 5) & (Te.vader <= -0.6) & (Te.review_text.str.split().str.len() <= 40)]
neg_hi = neg_hi.sample(min(3, len(neg_hi)), random_state=1)
pos_lo = pos_lo.sample(min(3, len(pos_lo)), random_state=1)
ex = pd.concat([neg_hi.assign(kind="1-2 stars but VADER strongly positive"), pos_lo.assign(kind="5 stars but VADER strongly negative")])
ex["excerpt"] = ex.review_text.map(trunc); ex[["kind", "rating", "vader", "excerpt"]].round(3).to_csv(TAB / "t16_disagreement_examples.csv", index=False)
R["vader_rating_disagreement"] = dict(low_rating_vader_positive_pct=float(((Te.rating <= 2) & (Te.vader >= 0.05)).sum() / (Te.rating <= 2).sum() * 100), high_rating_vader_negative_pct=float(((Te.rating >= 4) & (Te.vader <= -0.05)).sum() / (Te.rating >= 4).sum() * 100))
json.dump(R, open(RES / "w2_nlp_pilot.json", "w"), indent=1)
for k in ["baseline_majority", "vader", "tfidf_logreg", "tfidf_nb"]: print(k, "acc=%.3f macroF1=%.3f" % (R[k]["accuracy"], R[k]["macro_f1"]))
print("CV", R["logreg_cv_macro_f1"], "| n", R["sample_n"], "| overlap authors", R["author_overlap_train_test"], "| disagreement", R["vader_rating_disagreement"])
