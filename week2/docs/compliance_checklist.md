# Week 2 compliance checklist

Status: Done = completed with evidence in this repository; Partly = done in part; Student = needs your action.

## Official Week 2 requirements
| # | Requirement | Where | Status |
|---|---|---|---|
| 1 | DOC/DOCX report on the data sourcing strategy | `week2/report/YuvaIntern_Week2_Sephora_Data_Sourcing_Report.docx` | Done |
| 2 | List of potential sources with public dataset/API links | Report Table 5; `week2/docs/data_sources.md` | Done |
| 3 | Explicit initial exploratory analysis plan | Report Section 11 | Done |
| 4 | Expected statistical methods and visualisation techniques | Report Section 12; Figures 1-9 | Done |
| 5 | Data quality and relevance assessment | Report Sections 9, 10 | Done |
| 6 | Comparison of sources (advantages, disadvantages, accessibility, frequency, reliability) | Report Tables 6-8 | Done |
| 7 | How the data supports the Week 1 hypotheses | Report Section 14 (Table 24) | Done |
| 8 | Initial cleaning and preprocessing strategy | Report Section 16 (Table 26) | Done |

## Master-prompt deliverables
| Deliverable | Status |
|---|---|
| Final Week 2 DOCX | Done |
| Python inspection scripts (`week2/code/00-04`) | Done; all run on the full data |
| Data-quality notebook (`week2_data_quality_assessment.ipynb`, repository root) | Done; executed, saved with outputs |
| Data dictionary (`week2/docs/data_dictionary.md`, report Section 8) | Done |
| Source-comparison table | Done |
| Statistical analysis plan | Done (applied: descriptive, chi-square, Spearman, Wilson, Kruskal-Wallis; planned: Holm, regression) |
| NLP and sentiment strategy | Done; pilot experiment run (VADER, TF-IDF + LR, TF-IDF + NB) |
| Supporting figures and tables (`week2/figures`, `week2/tables`) | Done |
| Updated README, requirements.txt, .gitignore | Done |
| GitHub update instructions | Done (`git_update_commands.md`, repository root); nothing was pushed by the assistant |
| Submission description (at least 200 words) | Done (`submission_description.txt`, repository root) |

## Honesty checks
- Optional sources S2-S6 were **not** downloaded or analysed; the report says so.
- No production model was trained; the NLP part is a labelled pilot using weak labels.
- Week 1 hypotheses are unchanged.
- No scraping, no API access, no credentials in the repository.

## Student actions before submitting
- [ ] Check the Kaggle **licence** and **version** on the S1 page and add them to the report if you wish (the page text could not be read automatically).
- [ ] Open the .docx in Word and check page breaks.
- [ ] Check YuvaIntern's rules on AI-assisted work; be able to explain every table and the pilot.
- [ ] Run the notebook/scripts yourself once so you can reproduce the numbers.
- [ ] Push the files to GitHub (see `git_update_commands.md`) and confirm the repository is public.
- [ ] Upload the report and paste `submission_description.txt` into the form.
