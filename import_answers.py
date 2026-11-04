#!/usr/bin/env python3
"""Bring friends' answers from the public copies of the three basketball studies (pair at the root, realism/, value/;
answers go to one Formspree form with a `study` field) into the study's shared/choices.json, as Yulu's import_answers.py.
Accepts Formspree CSV exports, JSON files from "Download my answers", hand-wrapped {name, submitted_at, picks} JSON, or a
bare pasted `picks` list in <name>.txt. Valid answers per study come from studies_common.STUDIES. Latest submission per
name wins; existing entries are kept unless --replace; the store is backed up before writing.
  python3 import_answers.py --study pair|realism|value FILE... [--write] [--replace]
"""
import argparse, csv, glob, json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); HE = os.path.dirname(HERE); sys.path.insert(0, HE); from studies_common import STUDIES
DIRS = {"pair": "strategy_pair", "realism": "realism_clips", "value": "value_pairs"}
ap = argparse.ArgumentParser(); ap.add_argument("--study", choices=sorted(DIRS), required=True); ap.add_argument("files", nargs="+"); ap.add_argument("--write", action="store_true"); ap.add_argument("--replace", action="store_true"); a = ap.parse_args()
D = f"{HE}/{DIRS[a.study]}"; STORE = f"{D}/shared/choices.json"; STUDY = STUDIES[a.study]["study"]; VALID = {v for v, _ in STUDIES[a.study]["options"]}
SIDS = {it["id"] for it in json.load(open(f"{D}/manifest.json"))["items"]}
subs = []
def add(d, src):
    name = (d.get("name") or "").strip(); picks = d.get("picks")
    if isinstance(picks, str): picks = json.loads(picks) if picks.strip() else []
    if not name or not isinstance(picks, list): print(f"  skip (no name or picks): {src}"); return
    if d.get("study") and d["study"] != STUDY: print(f"  skip (study {d['study']!r} is not {STUDY}): {src}"); return
    subs.append((name, (d.get("submitted_at") or d.get("_date") or "")[:19], picks, src))
for pat in a.files:
    for f in sorted(glob.glob(pat)) or [pat]:
        if f.endswith(".json"): add(json.load(open(f)), f)
        elif f.endswith(".txt"): add({"name": os.path.basename(f)[:-4], "picks": open(f).read()}, f)
        elif f.endswith(".csv"):
            for n, row in enumerate(csv.DictReader(open(f, newline="", encoding="utf-8-sig"))):
                low = {k.strip().lower(): v for k, v in row.items() if k}
                add({"name": low.get("name"), "picks": low.get("picks"), "study": low.get("study"), "submitted_at": low.get("submitted_at") or low.get("submitted at") or low.get("_date") or low.get("date")}, f"{f}#{n+1}")
        else: sys.exit(f"unknown file type: {f}")
latest = {}
for name, at, picks, src in subs:
    if not at: at = max((p.get("at") or "" for p in picks), default="")[:19]
    if name not in latest or at > latest[name][0]: latest[name] = (at, picks, src)
store = json.load(open(STORE)) if os.path.exists(STORE) else {"ratings": {}}
R = store.setdefault("ratings", {}); new = {}
for name, (at, picks, src) in sorted(latest.items()):
    n_ok = n_skip = n_bad = 0
    for p in picks:
        sid, best = p.get("situation"), p.get("best")
        if sid not in SIDS or best not in VALID: n_bad += 1; continue
        k = f"{name}::{sid}"
        if k in R and not a.replace: n_skip += 1; continue
        new[k] = dict(best=best, note=(p.get("note") or "").strip(), at=(p.get("at") or at or "")[:19].replace("Z", ""), by=name, situation=sid, source=src, submitted_at=at); n_ok += 1
    print(f"{name:14s} latest submission {at or '(no time)'} from {src}: {len(picks)} picks -> {n_ok} to import, {n_skip} already in the store (kept), {n_bad} invalid; {sum(1 for x in subs if x[0] == name) - 1} older submission(s) ignored")
print(f"\n{len(new)} entries from {len(latest)} reviewer(s) for study {STUDY} -> {STORE}")
if not a.write: print("dry run: nothing written (add --write)"); sys.exit(0)
if os.path.exists(STORE): shutil.copy(STORE, f"{STORE[:-5]}.backup_{time.strftime('%Y%m%d_%H%M%S')}.json")
R.update(new); store["saved_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
tmp = STORE + ".tmp"; json.dump(store, open(tmp, "w"), indent=1); os.replace(tmp, STORE)
print(f"written: {STORE} now holds {len(R)} entries")
