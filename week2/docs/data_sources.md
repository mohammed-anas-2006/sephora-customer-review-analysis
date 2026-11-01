# Data sources evaluated in Week 2

Links were opened on 31 October 2026. "Verified" means the fact was read on the page named; anything not verified is marked. No source other than S1 has been downloaded or analysed.

| ID | Source | Link | Type | Independence | Status |
|---|---|---|---|---|---|
| S1 | Kaggle - Sephora Products and Skincare Reviews (N. Inky) | https://www.kaggle.com/datasets/nadyinky/sephora-products-and-skincare-reviews | Reviews + product catalogue | Primary collection (scraped from sephora.com) | **Primary source; downloaded and analysed** |
| S2 | Kaggle - Sephora Skincare Reviews & Sentiment (N. Messier) | https://www.kaggle.com/datasets/natashamessier/sephora-skincare-reviews-and-sentiment | Reviews sample + product info + VADER sentiment | Separate scrape of the same retailer | Link valid; not downloaded |
| S3 | Hugging Face mirror of S2 (haoxianc) | https://huggingface.co/datasets/haoxianc/natashamessier_sephora-skincare-reviews-and-sentiment | Same files as S2 | **Mirror of S2 - not independent** | Link valid; not downloaded |
| S4 | Amazon Reviews 2023 (McAuley Lab) | https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023 | Reviews + item metadata (Amazon) | Independent retailer | Facts read from dataset card; not downloaded |
| S5 | Google Trends | https://trends.google.com/trends/ (method: https://support.google.com/trends/answer/4365533) | Normalised search interest | Independent signal | Method page verified; not used |
| S6 | Reddit Data API | https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki | Posts and comments | Independent signal | Rules verified; no access requested |

## Key facts per source

**S1 (primary).** Verified in the supplied files: 5 review CSVs with identical 19 columns (1,094,411 reviews, 2,351 skincare products, 142 brands, 2008-08-28 to 2023-03-21) plus `product_info.csv` (8,494 products, 27 columns). The Kaggle page meta-description reads: "Info about 8k+ products and about 1 mln user reviews from the Skincare category." The licence field could not be read from the retrievable page content: check it on Kaggle. Data originate from sephora.com, so Sephora's terms may also apply. Recommendation labels exist only from 2017; reviews cover skincare only.

**S2 / S3.** From the Hugging Face dataset card: 40,234 reviews across 2,012 skincare products scraped from sephora.com; up to 10 most recent reviews per product; includes marketing labels (clean, planet aware, vegan, cruelty-free, luxury) and VADER sentiment/polarity scores; MIT licence stated for the original Kaggle dataset. The preview shows reviews dated into 2025. S3 is tagged `kaggle-mirror`; its dataset viewer fails because the three CSV files have different columns, so load files individually.

**S4.** From the dataset card: Beauty_and_Personal_Care has 11.3M users, 1.0M items and 23.9M ratings; All_Beauty has 632.0K users, 112.6K items and 701.5K ratings; interactions span May 1996 to Sep 2023; review fields include rating, title, text, timestamp, helpful_vote and verified_purchase. No recommendation flag. Citation: Hou, Y., Li, J., He, Z., Yan, A., Chen, X., McAuley, J. (2024), arXiv:2403.03952. Terms not verified: check the dataset page.

**S5.** From Google's FAQ: Trends is a largely unfiltered sample of actual searches, anonymised and aggregated; each data point is divided by total searches and scaled 0-100; low-volume searches appear as 0; statistical noise is added; it is not a scientific poll.

**S6.** From the Reddit Data API Wiki: use is subject to Reddit's Developer Terms and Data API Terms; OAuth2 authentication; a unique descriptive User-Agent; 100 queries per minute per OAuth client ID for free access; commercial access and research approval must be requested. No scraping or bypassing limits. Credentials must never be committed to the repository.

## Decision
S1 is the primary source because it is the only candidate that supports all three Week 1 hypotheses (ratings, recommendation label, review text, brands, customer attributes) at scale. S4 (cross-platform check), S5 (interest over time) and S6 (vocabulary) are optional supplementary sources for later weeks. S2 may serve as a small secondary Sephora comparison; do not use S2 and S3 together as separate evidence.
