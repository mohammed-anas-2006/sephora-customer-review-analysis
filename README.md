# Sephora Customer Review Analysis

**YuvaIntern - Data Science with Python Analyst Internship, Week 1**
Author: Mohammed Anas (AIML, P A College of Engineering, Mangalore)

An exploratory data analysis of customer satisfaction and product-recommendation behaviour in the beauty industry, using Sephora skincare reviews. The full write-up is in [`report/YuvaIntern_Week1_Sephora_Report_Final.docx`](report/YuvaIntern_Week1_Sephora_Report_Final.docx).

## Problem statement
Beauty retailers receive thousands of reviews per product but cannot read them all. How can review data be used to measure customer satisfaction, understand when satisfied customers actually recommend a product, and identify the recurring complaints that signal dissatisfaction?

## Dataset
Kaggle: *Sephora Products and Skincare Reviews* (Nady Inky, 2023) - https://www.kaggle.com/datasets/nadyinky/sephora-products-and-skincare-reviews

The CSV files are **not** included in this repository (they are large, and the Kaggle licence/terms apply - please check them on the dataset page). Download them and place these six files in a `data/` folder at the repository root:
`reviews_0-250.csv`, `reviews_250-500_1.csv`, `reviews_500-750_1.csv`, `reviews_750-1250_1.csv`, `reviews_1250-end.csv`, `product_info.csv`
(if your downloaded names have a numeric prefix, the scripts still find them; only `product_info.csv` must have exactly that name).

## Tools
Python 3, Pandas, NumPy, SciPy (chi-square test, Spearman correlation), Matplotlib, Jupyter / Google Colab.

## Methodology
1. Inspect and combine the five review files; check structure, duplicates and missing values.
2. Recompute the results from the initial 1,000-row sample and compare them with the full data.
3. Describe rating and recommendation distributions; test the association between rating and recommendation (chi-square, Spearman).
4. Compare brands, products, price bands and customer characteristics, always with sample sizes.
5. Count complaint keyword groups in 1-2 star reviews versus all 5-star reviews (keyword matching only).

## Verified findings (all 1,094,411 reviews; 2,351 products; 142 brands)
- 63.9% of reviews are 5-star, 82.1% are 4 or 5 stars, 10.4% are 1 or 2 stars; mean rating 4.30.
- 778,160 reviews recommend the product, 148,263 do not, and 167,988 (15.4%) have no recommendation value; 84.0% of reviews with a recorded decision recommend.
- Recommendation rate by star rating: 0.77%, 3.67%, 35.66%, 96.57%, 99.86% (1 to 5 stars). Spearman rho = 0.72. This is an association, not causation.
- The initial 1,000-row sample (999 LANEIGE reviews, 1 NUDESTIX review) was reproduced exactly, but it is not representative: e.g. the 3-star recommendation rate is 27.4% in the sample versus 35.7% in the full data.
- Price has no meaningful relationship with rating (Spearman 0.008).
- "No visible effect" phrases appear in 12.8% of 1-2 star reviews versus 0.5% of 5-star reviews.

## Limitations
Self-selected reviewers and skewed ratings; 15.4% of recommendation values missing; very unequal review counts per product and brand; one retailer, skincare reviews up to March 2023; keyword matching cannot detect negation or context; brand/product differences are descriptive and not significance-tested. **No machine-learning, sentiment or topic model was built.**

## Reproduce
```bash
pip install -r requirements.txt
python code/analysis.py       # -> code/results.json
python code/themes_full.py    # adds keyword themes to code/results.json (reads text in chunks)
python code/make_charts.py    # -> charts/fig1 ... fig7
```
or open `code/sephora_week1_analysis.ipynb` (saved with its outputs from a run on the full dataset; about 6-8 GB RAM needed, use a high-RAM runtime on Colab).

## Structure
```
README.md   requirements.txt   project_description.txt
code/    analysis.py  themes_full.py  make_charts.py  sephora_week1_analysis.ipynb  results.json
charts/  fig1 ... fig7 (PNG)
report/  YuvaIntern_Week1_Sephora_Report_Final.docx
data/    (not included - download from Kaggle)
```
