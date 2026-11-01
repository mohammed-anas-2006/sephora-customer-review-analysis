# Sephora Customer Review Analysis

**YuvaIntern Data Science with Python Analyst Internship**
**Author:** Mohammed Anas, Artificial Intelligence and Machine Learning, P A College of Engineering, Mangalore

This project analyses Sephora skincare reviews to describe customer ratings, recommendation behaviour, and recurring review themes. Week 1 established the exploratory analysis; Week 2 documented and assessed the source data, added statistical checks, and ran a small sentiment-classification feasibility pilot. The work is descriptive and observational. It does not establish causation or provide a production sentiment model.

## Research questions

The Week 1 hypotheses are retained:

- **H1:** Higher product ratings are associated with higher recommendation rates.
- **H2:** Negative reviews contain recurring complaint themes that may indicate product or customer-experience problems.
- **H3:** Customer feedback patterns differ across products and brands.

## Week 1: exploratory analysis

Week 1 combined five review CSV files containing 1,094,411 reviews, covering 2,351 products and 142 brands. It compared an initial 1,000-review sample with the full review set, summarized ratings and recommendation behaviour, examined product and brand patterns, and used keyword groups to compare themes in low-rated and five-star review text.

- 63.9% of reviews are five-star; 82.1% are four- or five-star. The mean rating is 4.30.
- Among reviews with a recorded recommendation decision, the recommendation rate ranges from 0.8% for one-star reviews to 99.9% for five-star reviews. Spearman's rho is about 0.72. This is an association, not a causal effect.
- The keyword theme counts are exploratory matches, not results from a trained sentiment model.

See [the Week 1 report](report/YuvaIntern_Week1_Sephora_Report_Final.docx), [`code/`](code/), and [`charts/`](charts/).

## Week 2: sourcing, quality, statistics, and NLP pilot

Week 2 compared six candidate sources: two Kaggle Sephora datasets, a Hugging Face mirror, Amazon Reviews 2023, Google Trends, and the Reddit Data API. The mirror is not independent evidence. The primary source is Kaggle's [Sephora Products and Skincare Reviews](https://www.kaggle.com/datasets/nadyinky/sephora-products-and-skincare-reviews); the other sources were evaluated as candidates and were not downloaded for analysis.

The six primary CSV files were inventoried and assessed across eight data-quality dimensions. Findings include skincare-only review coverage, recommendation values absent for all reviews before 2017, 64 placeholder reviewer IDs, 224 exact duplicate rows, and small brand-level rating differences. For the 926,423 reviews with recorded recommendations, rating and recommendation are strongly associated (chi-square = 741,794, 4 degrees of freedom; Cramér's V = 0.895). Across 95 brands with at least 1,000 reviews, the Kruskal-Wallis result is H = 18,073, p < 0.001, with epsilon-squared about 0.017, a small effect. The analysis reports effect sizes and confidence intervals alongside p-values. Holm-corrected post-hoc brand comparisons are planned, not completed. The data dictionary and report document the planned cleaning and text-preprocessing steps.

The NLP work is a feasibility pilot on 99,867 reviews. Labels were derived from star ratings (1-2 negative, 3 neutral, 4-5 positive); they are weak labels, not human-verified sentiment. The reviewer-grouped holdout contained no reviewer in both sets. TF-IDF with logistic regression achieved macro-F1 0.706 (three-fold grouped cross-validation mean 0.704); TF-IDF with multinomial Naive Bayes achieved 0.649; VADER achieved 0.452. These scores measure agreement with star-derived labels and do not establish production model quality.

See the [Week 2 report](week2/report/YuvaIntern_Week2_Sephora_Data_Sourcing_Report.docx), [data sources](week2/docs/data_sources.md), [data dictionary](week2/docs/data_dictionary.md), [compliance checklist](week2/docs/compliance_checklist.md), and [Week 2 notebook](week2_data_quality_assessment.ipynb).

## Project structure

```text
README.md
requirements.txt
.gitignore
project_description.txt
submission_description.txt
week2_data_quality_assessment.ipynb
charts/                         Week 1 figures
code/                           Week 1 scripts, results, and notebook
report/                         Week 1 report
week2/
  code/                         Checksums, inventory, statistics, NLP, figures
  results/                      Saved JSON analysis results
  tables/                       CSV tables, including pilot metrics and confusion matrices
  figures/                       Week 2 PNG figures
  docs/                         Sources, dictionary, compliance notes
  report/                       Week 2 DOCX report
data/                            Local source CSVs; excluded from this repository
```

The raw CSV files are intentionally excluded because of their size and applicable source terms. Before running data-dependent code, download the five review CSVs and `product_info.csv` from the primary source into `data/`. The review files may have numeric prefixes in their names; `product_info.csv` must retain that exact filename. Compare downloaded files with `week2/tables/t00_file_checksums.csv`.

## Technologies

Python 3, pandas, NumPy, SciPy, Matplotlib, scikit-learn, vaderSentiment, and Jupyter. Install the declared packages with:

```bash
python -m pip install -r requirements.txt
```

## Running the project

Run commands from the repository root. Week 1 analysis and chart commands require the source CSVs:

```bash
python code/analysis.py
python code/themes_full.py
python code/make_charts.py
```

Run the Week 2 scripts in order:

```bash
python week2/code/00_file_checksums.py
python week2/code/01_data_inventory.py
python week2/code/02_stats_and_text_profile.py
python week2/code/03_nlp_pilot.py
python week2/code/04_make_week2_figures.py
```

The checksum, inventory, statistics, and NLP steps need the local source files. The NLP step also needs all dependencies from `requirements.txt`. The final figure step reads the saved JSON results and tables produced by the earlier steps. Both notebooks include saved outputs; rerun them from top to bottom after placing the data locally.

## Limitations and next steps

The reviews are self-selected and strongly skew positive. They cover Sephora skincare only and end on 21 March 2023. Recommendation values are structurally missing before 2017. Review volume is highly unequal across products and brands, and repeat reviewers mean simple inferential tests may overstate precision. The sentiment pilot uses star-derived labels that may disagree with a person's sentiment. No human-labelled validation set or production model was created. Optional sources were not analysed. Planned work includes a cleaning log, human-validated labels, corrected post-hoc comparisons, and a carefully scoped supplementary source after its terms are checked.
