# Data dictionary

Column names and types come from the original files as read by Pandas (pandas 3.x). Descriptions marked *(inferred)* come from column names and observed values, because a formal dictionary could not be retrieved from the Kaggle page. Missing percentages and counts are exact values from the files (Week 2, script `01_data_inventory.py`).

## Review files (5 files, 19 columns each, 1,094,411 rows in total)

| Column | Data type | Description | Analytical role | Quality concerns |
|---|---|---|---|---|
| Unnamed: 0 | int64 | Row counter restarting at 0 in each file | Not used | Not unique across files |
| author_id | text (int64 in 1,094,347 rows) | Pseudonymous reviewer identifier | Counting reviewers; grouping for train/test splits | 64 rows hold placeholders ("orderGen…", "dummyUser"); 503,216 distinct values |
| rating | int64 | Star rating, 1 to 5 | Main outcome (ordinal) | No invalid values; strongly left-skewed (skewness -1.68) |
| is_recommended | float64 (1.0, 0.0, blank) | Whether the reviewer recommends the product | Binary outcome (H1) | 15.35% missing; blank for all of 2008 to 2016 |
| helpfulness | float64 | Share of voters who rated the review helpful (positive votes / total votes) | Context only | 51.31% undefined because no one voted |
| total_feedback_count | int64 | Total helpfulness votes | Context | 51.3% of reviews have 0 votes |
| total_neg_feedback_count | int64 | Negative helpfulness votes | Context | Equals total minus positive in 100% of rows |
| total_pos_feedback_count | int64 | Positive helpfulness votes | Context | As above |
| submission_time | text (YYYY-MM-DD) | Date the review was posted | Time analysis (convert to date) | 2008-08-28 to 2023-03-21; 2023 is partial |
| review_text | text | Body of the review | NLP, complaint themes (H2) | 1,444 missing (0.13%); may mention star ratings |
| review_title | text | Review headline | Optional NLP feature | 28.39% missing |
| skin_tone | text | Self-reported skin tone (14 labels) | Customer attribute (H3) | 15.58% missing; "notSureST" (70) is a placeholder; "ebony" has 3 reviews |
| eye_color | text | Self-reported eye colour (6 labels) | Customer attribute | 19.15% missing; "Grey" (4,859) and "gray" (621) are separate labels |
| skin_type | text | Self-reported skin type (4 labels) | Customer attribute (H3) | 10.19% missing |
| hair_color | text | Self-reported hair colour (7 labels) | Customer attribute | 20.72% missing; "brown" and "brunette" overlap |
| product_id | text | Sephora product identifier (for example P379064) | Key to product_info.csv | All 2,351 IDs found in the catalogue |
| product_name | text | Product name | Label | 17 names are shared by more than one product ID |
| brand_name | text | Brand name | Grouping (H3) | 142 brands; no variants after case-folding |
| price_usd | float64 | Price in US dollars | Explanatory variable | Identical to the catalogue price for all 2,351 products: a snapshot, not the price on the review date |

## product_info.csv (27 columns, 8,494 rows)

| Column | Data type | Description | Analytical role | Quality concerns |
|---|---|---|---|---|
| product_id | text | Unique product key | Join key | Unique; matches all reviews |
| product_name | text | Product name | Label | Complete |
| brand_id | int64 | Numeric brand ID (inferred) | Grouping | Complete |
| brand_name | text | Brand name | Grouping | 304 brands |
| loves_count | int64 | Count of "loves" or favourites (inferred) | Popularity proxy | Complete |
| rating | float64 | Average product rating on the site (inferred) | Cross-check with review means | 3.27% missing |
| reviews | float64 | Number of reviews listed on the site (inferred) | Completeness cross-check | 3.27% missing |
| size | text | Pack size | Optional | 19.20% missing |
| variation_type | text | Type of variant (inferred) | Optional | 17.00% missing |
| variation_value | text | Variant value (inferred) | Optional | 18.81% missing |
| variation_desc | text | Variant description (inferred) | Not used | 85.28% missing |
| ingredients | text | Ingredient list | Future ingredient analysis | 11.13% missing |
| price_usd | float64 | Price in US dollars | Price bands | Complete, all positive |
| value_price_usd | float64 | Reference ("value") price (inferred) | Not used | 94.69% missing |
| sale_price_usd | float64 | Sale price (inferred) | Not used | 96.82% missing |
| limited_edition | int64 | Flag (0/1) | Optional | Complete |
| new | int64 | Flag (0/1) | Optional | Complete |
| online_only | int64 | Flag (0/1) | Optional | Complete |
| out_of_stock | int64 | Flag (0/1) | Optional | Complete |
| sephora_exclusive | int64 | Flag (0/1) | Optional | Complete |
| highlights | text | Marketing highlight tags (inferred) | Marketing-claim analysis | 25.98% missing |
| primary_category | text | Top-level category (9 values) | Coverage check | Complete |
| secondary_category | text | Second-level category | Product-type grouping | 0.09% missing |
| tertiary_category | text | Third-level category | Product-type grouping | 11.66% missing |
| child_count | int64 | Number of child variants (inferred) | Not used | Complete |
| child_max_price | float64 | Highest child price (inferred) | Not used | 67.58% missing |
| child_min_price | float64 | Lowest child price (inferred) | Not used | 67.58% missing |
