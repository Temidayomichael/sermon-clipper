"""Stock B-roll from Pexels or Pixabay (both free for commercial use): search, pick, download and cache clips.

Graphics that need footage carry a search `query`:
  - {"type": "insert", "query": "..."}   quick full-screen insert on a concrete word
  - {"type": "split",  "query": "..."}   pastor on top, B-roll below
  - {"type": "cutaway", "visual": "stock:<query>"}   full-screen cutaway with real footage
  - {"type": "cutaway", "visual": "<illustration>", "stock_query": "..."}   real footage, illustration as fallback
The chosen clip is stored on the graphic as g["stock"] and cached in assets/broll_cache/.
Set a key in config.json: "pexels_api_key" (PEXELS_API_KEY) or "pixabay_api_key" (PIXABAY_API_KEY).
Pexels is used when its key is set, otherwise Pixabay. No key? Put your own clips in assets/broll/ and
use visual "broll:<file>".
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .common import ASSETS, config, job_dir, read_json, write_json

CACHE = ASSETS / "broll_cache"
ENDPOINTS = ["https://api.pexels.com/videos/search", "https://api.pexels.com/v1/videos/search"]
UA = "sermon-clipper (https://github.com/Temidayomichael/sermon-clipper)"


def pexels_key() -> str | None:
    return os.environ.get("PEXELS_API_KEY") or config().get("pexels_api_key") or None


def pixabay_key() -> str | None:
    return os.environ.get("PIXABAY_API_KEY") or config().get("pixabay_api_key") or None


def api_key() -> str | None:
    return pexels_key() or pixabay_key()


def search_pixabay(query: str, need: float, key: str) -> list[dict]:
    params = urllib.parse.urlencode({"key": key, "q": query, "video_type": "film", "safesearch": "true", "per_page": 30})
    try:
        req = urllib.request.Request(f"https://pixabay.com/api/videos/?{params}", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            hits = json.loads(r.read()).get("hits", [])
    except urllib.error.HTTPError as e:
        if e.code in (400, 401, 403):
            raise SystemExit("Pixabay rejected the request. Check pixabay_api_key in config.json.")
        if e.code == 429:
            raise SystemExit("Pixabay rate limit reached. Try again in a minute.")
        raise
    cands = []
    for v in hits:
        vids = v.get("videos", {})
        f = next((vids[k] for k in ("large", "medium") if vids.get(k, {}).get("url") and min(vids[k]["width"], vids[k]["height"]) >= 1080), None) \
            or next((vids[k] for k in ("large", "medium", "small") if vids.get(k, {}).get("url")), None)
        if not f:
            continue
        portrait = f["height"] > f["width"]
        hd = min(f["width"], f["height"]) >= 1080
        score = (2 if portrait else 0) + (1 if v.get("duration", 0) >= need else -2) + (1 if hd else 0)
        cands.append({
            "id": f"pixabay-{v['id']}", "score": score, "duration": v.get("duration", 0),
            "thumb": f.get("thumbnail") or "", "page": v.get("pageURL", ""),
            "credit": v.get("user", ""), "credit_url": "", "link": f["url"], "portrait": portrait, "source": "Pixabay",
        })
    cands.sort(key=lambda c: -c["score"])
    return cands[:8]


def query_of(g: dict) -> str | None:
    if g.get("type") in ("insert", "split"):
        return g.get("query")
    if g.get("type") == "cutaway" and str(g.get("visual", "")).startswith("stock:"):
        return g["visual"][6:]
    if g.get("type") == "cutaway" and g.get("stock_query"):
        return g["stock_query"]  # real footage replaces the illustration once found; the illustration stays as fallback
    return None


def _get(url: str, key: str) -> dict:
    req = urllib.request.Request(url, headers={"Authorization": key, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def search(query: str, need: float = 4.0) -> list[dict]:
    """Best candidate clips for a query: portrait first, long enough, HD, not huge."""
    key = pexels_key()
    if not key:
        if pixabay_key():
            return search_pixabay(query, need, pixabay_key())
        raise SystemExit(
            "No stock footage key. Create a free key at https://pixabay.com/api/docs/ (or Pexels) and add it to config.json as\n"
            '  "pixabay_api_key": "<your key>"   (config.json is never committed)'
        )
    videos = []
    for orientation in ("portrait", "landscape"):
        params = urllib.parse.urlencode({"query": query, "orientation": orientation, "size": "medium", "per_page": 15})
        for ep in ENDPOINTS:
            try:
                videos += _get(f"{ep}?{params}", key).get("videos", [])
                break
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue
                if e.code in (401, 403):
                    raise SystemExit("Pexels rejected the API key. Check pexels_api_key in config.json.")
                if e.code == 429:
                    raise SystemExit("Pexels rate limit reached (200 searches/hour). Try again later.")
                raise
        if len(videos) >= 6:
            break

    cands = []
    seen = set()
    for v in videos:
        if v["id"] in seen:
            continue
        seen.add(v["id"])
        files = [f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and f.get("width") and f.get("height")]
        good = [f for f in files if min(f["width"], f["height"]) >= 1080] or files
        if not good:
            continue
        f = min(good, key=lambda f: f["width"] * f["height"])  # smallest file that is still HD
        portrait = v["height"] > v["width"]
        score = (2 if portrait else 0) + (1 if v.get("duration", 0) >= need else -2) + (1 if min(f["width"], f["height"]) >= 1080 else 0)
        cands.append({
            "id": v["id"],
            "score": score,
            "duration": v.get("duration", 0),
            "thumb": v.get("image"),
            "page": v.get("url"),
            "credit": v.get("user", {}).get("name", ""),
            "credit_url": v.get("user", {}).get("url", ""),
            "link": f["link"],
            "portrait": portrait,
            "source": "Pexels",
        })
    cands.sort(key=lambda c: -c["score"])
    return cands[:8]


def download(cand: dict) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    cid = str(cand["id"])
    name = f"{cid if cid.startswith('pixabay-') else 'pexels-' + cid}.mp4"
    out = CACHE / name
    if not out.exists():
        req = urllib.request.Request(cand["link"], headers={"User-Agent": UA})
        tmp = out.with_suffix(".part")
        with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        tmp.rename(out)
    return name


def choose(g: dict, index: int) -> None:
    """Point graphic g at candidate `index` (searching first if needed) and download it."""
    q = query_of(g)
    st = g.get("stock") or {}
    if st.get("query") != q or not st.get("candidates"):
        need = float(g.get("duration", 4))
        st = {"query": q, "candidates": search(q, need)}
    if not st["candidates"]:
        g["stock"] = {"query": q, "candidates": [], "error": "no results"}
        return
    index %= len(st["candidates"])
    c = st["candidates"][index]
    st.update({"choice": index, "file": download(c), "thumb": c["thumb"], "credit": c["credit"], "page": c["page"],
               "source": c.get("source", "Pexels")})
    g["stock"] = st


def resolve_job(job: str, only_missing: bool = True) -> int:
    """Find and download stock footage for every graphic that needs it. Returns how many were fetched."""
    p = job_dir(job) / "plan.json"
    plan = read_json(p)
    n = 0
    for c in plan["clips"]:
        if c.get("status") == "dropped":
            continue
        for g in c.get("graphics", []):
            q = query_of(g)
            if not q:
                continue
            st = g.get("stock") or {}
            if only_missing and st.get("query") == q and st.get("file") and (CACHE / st["file"]).exists():
                continue
            print(f"  B-roll for {c['id']}: '{q}'")
            choose(g, st.get("choice", 0) if st.get("query") == q else 0)
            n += 1
    write_json(p, plan)
    return n


def next_clip(job: str, clip_id: str, gi: int) -> dict:
    """Swap one graphic's footage for the next search result."""
    p = job_dir(job) / "plan.json"
    plan = read_json(p)
    c = next(c for c in plan["clips"] if c["id"] == clip_id)
    g = c["graphics"][gi]
    choose(g, (g.get("stock") or {}).get("choice", -1) + 1)
    write_json(p, plan)
    return g["stock"]


def credits(c: dict) -> list[str]:
    out = []
    for g in c.get("graphics", []):
        st = g.get("stock") or {}
        if st.get("file") and st.get("credit"):
            out.append(f"{st['credit']} on {st.get('source', 'Pexels')} ({st.get('page', '')})")
    return out
