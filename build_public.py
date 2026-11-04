#!/usr/bin/env python3
"""Static, shareable copies of the three basketball studies for GitHub Pages (the basketball counterpart of Yulu's
strategy_pair/build_public.py + build_public_study.py): fills public_studies/ (pair at the ROOT, realism/, value/) with
index.html = studies_common.render(study, SERVER=false, endpoint) and a bland manifest (opaque ids, nothing from the
answer key). Videos: copied as the private pages serve them (864x496, crf 20) into --videos-out (default <root>/videos
or <root>/<study>/videos), first frames -> JPEG; with --video-base the manifest points at absolute URLs (Cloudflare R2 or
any host) and the repo holds only the pages. Idempotent for the videos.
  python3 build_public.py --study pair|realism|value [--endpoint https://formspree.io/f/<id>] [--videos-out DIR] [--video-base URL] [--jobs 4]
"""
import argparse, concurrent.futures, datetime, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); HE = os.path.dirname(HERE); sys.path.insert(0, HE); from studies_common import render
DIRS = {"pair": ("strategy_pair", "strategy_pair_private", ""), "realism": ("realism_clips", "realism_clips_private", "realism"), "value": ("value_pairs", "value_pairs_private", "value")}
ap = argparse.ArgumentParser(); ap.add_argument("--study", choices=sorted(DIRS), required=True); ap.add_argument("--endpoint", default="https://formspree.io/f/REPLACE_ME"); ap.add_argument("--jobs", type=int, default=4)
ap.add_argument("--videos-out", default=None); ap.add_argument("--video-base", default=""); a = ap.parse_args()
SRC, PRIV, SUB = (f"{HE}/{DIRS[a.study][0]}", f"{HE}/{DIRS[a.study][1]}", DIRS[a.study][2]); OUT = f"{HERE}/{SUB}" if SUB else HERE
VOUT = a.videos_out or f"{OUT}/videos"; os.makedirs(VOUT, exist_ok=True); os.makedirs(OUT, exist_ok=True)
def url(name): return f"{a.video_base.rstrip('/')}/{name}" if a.video_base else f"videos/{name}"
M = json.load(open(f"{SRC}/manifest.json")); jobs = []; items = []
for it in M["items"]:
    item = dict(id=it["id"]); vids = []
    if it.get("first"):
        jpg = f"{it['id']}_first.jpg"
        if not os.path.exists(f"{VOUT}/{jpg}"): jobs.append(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", os.path.realpath(f"{SRC}/{it['first']}"), "-q:v", "3", f"{VOUT}/{jpg}"])
        item["first"] = url(jpg)
    for v in it["videos"]:
        target = os.path.realpath(f"{SRC}/{v['src']}"); assert PRIV in target, target
        name = os.path.basename(v["src"]); out = f"{VOUT}/{name}"
        if not os.path.exists(out) or os.path.getsize(out) != os.path.getsize(target): jobs.append(["cp", target, out])
        vids.append(dict(letter=v["letter"], src=url(name)))
    item["videos"] = vids; items.append(item)
fails = []
with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
    for cmd, r in zip(jobs, ex.map(lambda c: subprocess.run(c, capture_output=True, text=True), jobs)):
        if r.returncode: fails.append((cmd[-1], r.stderr[-200:]))
assert not fails, fails
open(f"{OUT}/index.html", "w").write(render(a.study, False, a.endpoint))
json.dump(dict(built=datetime.date.today().isoformat(), sport=M["sport"], task=M["task"], items=items), open(f"{OUT}/manifest.json", "w"), indent=1)
json.dump(dict(built=datetime.date.today().isoformat(), study=a.study, endpoint=a.endpoint, source_manifest_built=M["built"], n_items=len(items), path=f"/{SUB}/" if SUB else "/", videos_out=VOUT, video_base=a.video_base), open(f"{PRIV}/public_copy_build.json", "w"), indent=1)
mb = sum(os.path.getsize(f"{VOUT}/{f}") for f in os.listdir(VOUT)) / 2**20
print(f"{a.study}: {len(jobs)} files made/copied, {sum(len(i['videos']) for i in items)} videos in {VOUT} ({mb:.0f} MB), manifest src = {items[0]['videos'][0]['src']}, {OUT}/index.html (SERVER=false, endpoint {a.endpoint}), manifest.json ({len(items)} items)")
