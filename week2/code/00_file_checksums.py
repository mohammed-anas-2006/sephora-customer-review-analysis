"""Week 2 - Step 0: record file names, sizes and SHA-256 checksums of the raw files (reproducibility record).

Run:  python week2/code/00_file_checksums.py   ->  week2/tables/t00_file_checksums.csv
Re-run after downloading the data; identical hashes mean you are analysing the same files used in the report.
"""
import glob, hashlib, os, sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
review_files = sorted(glob.glob(str(DATA / "*reviews_*.csv")))
product_file = DATA / "product_info.csv"
if len(review_files) != 5 or not product_file.is_file():
    print(
        "Expected five review CSV files and data/product_info.csv. "
        "Download the source files before running this step; existing checksum "
        "results were left unchanged.",
        file=sys.stderr,
    )
    raise SystemExit(2)

rows = []
for f in sorted([*review_files, str(product_file)]):
    h = hashlib.sha256()
    with open(f, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""): h.update(blk)
    name = os.path.basename(f); name = name.split("_", 1)[1] if name[0].isdigit() else name
    rows.append(dict(file=name, bytes=os.path.getsize(f), sha256=h.hexdigest()))
out = ROOT / "week2" / "tables"; out.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(out / "t00_file_checksums.csv", index=False); print(pd.DataFrame(rows).to_string(index=False))
