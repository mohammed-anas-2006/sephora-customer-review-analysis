"""Keyword-theme counts in 1-2 star reviews versus ALL 5-star reviews (keyword matching, not a sentiment model).

Run after analysis.py:  python code/themes_full.py
Reads the review text in chunks (low memory) and adds theme results to code/results.json.
"""
import glob, json
from collections import Counter
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "code" / "results.json"
THEMES = {
 "breakout / acne": r"\bbreak(?:ing|s)?[ -]?outs?\b|\bacne\b|\bpimples?\b|\bzits?\b|\bclogg?(?:ed|ing|s)?\b|\bcomedones?\b",
 "irritation / burning / rash": r"\birritat\w*|\bburn(?:s|ed|ing|t)?\b|\bsting(?:s|ing)?\b|\brash(?:es)?\b|\bredness\b|\bitch\w*|\ballerg\w*|\breaction\b",
 "dryness / oiliness / heavy feel": r"\bdry(?:ness|ing)?\b|\bgreasy\b|\boily\b|\bsticky\b|\btacky\b|\bheavy\b",
 "no visible effect": r"didn.?t work|did not work|doesn.?t work|does not work|no (?:noticeable )?(?:difference|effect|results?|improvement)|did nothing|waste of|not effective|ineffective",
 "smell / fragrance": r"\bsmell\w*|\bscent\w*|\bfragranc\w*|\bodou?r\b",
 "price / value": r"\bexpensive\b|\boverpriced\b|\bprice\b|\bpricey\b|\bworth\b",
 "packaging / leaking / pump": r"\bpackag\w*|\bleak\w*|\bpump\b|\bbroke\b|\bbroken\b|\bdispens\w*|\bspill\w*",
 "pilling / flaking / residue": r"\bpill(?:s|ing|ed)?\b|\bflak\w*|\bresidue\b|\bcaked?\b|\bcaking\b",
}
STOP = set("the and for that this with was have but not you are they had has its it's from just my very like get got would one out use used when product products will there than then them what been more into after about because only other also any can too still even all did does were which their your she her him his how why who our over really".split())
files = sorted(glob.glob(str(ROOT / "data" / "*reviews_*.csv")))
cnt = {g: {"neg": 0, "five": 0} for g in THEMES}
N = {"neg": 0, "five": 0}; words = Counter()
for f in files:
    for ch in pd.read_csv(f, usecols=["rating", "review_text"], chunksize=100_000):
        ch = ch.dropna(subset=["review_text"])
        for key, mask in (("neg", ch.rating <= 2), ("five", ch.rating == 5)):
            txt = ch.review_text[mask].str.lower(); N[key] += len(txt)
            for g, rx in THEMES.items():
                cnt[g][key] += int(txt.str.contains(rx, regex=True).sum())
            if key == "neg":
                for t in txt: words.update(w for w in re.findall(r"[a-z]{3,}", t) if w not in STOP)
R = json.load(open(RES))
R["neg_n"] = N["neg"]; R["five_star_text_n"] = N["five"]
R["themes_neg"] = {g: [c["neg"], round(100 * c["neg"] / N["neg"], 1)] for g, c in cnt.items()}
R["themes_pos_pct"] = {g: round(100 * c["five"] / N["five"], 1) for g, c in cnt.items()}
R["neg_words"] = words.most_common(25)
json.dump(R, open(RES, "w"), indent=1, default=str)
print("1-2 star reviews with text:", N["neg"], "| 5-star reviews with text:", N["five"])
for g in THEMES: print(f"{g:34s} low-rated {R['themes_neg'][g][1]:5.1f}%   5-star {R['themes_pos_pct'][g]:5.1f}%")
