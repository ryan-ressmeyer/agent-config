"""Shared helpers for the lit-discovery scripts. stdlib only."""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ANSA_URL = os.environ.get("ANSA_URL", "http://kamaji:7327")
CONTACT_EMAIL = os.environ.get("ANSA_CONTACT_EMAIL", "ryan.ressmeyer@gmail.com")
USER_AGENT = f"ansa-lit-discover/0.1 (mailto:{CONTACT_EMAIL})"


def http_json(url, *, method="GET", body=None, headers=None, retries=3, timeout=30):
    h = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        h.update(headers)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, method=method, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:
            last = e
            time.sleep(1.0 * (attempt + 1))
    raise last


def ansa_lookup_doi(doi):
    """Return (ansa_id, citekey) if a paper with this DOI exists, else (None, None)."""
    if not doi:
        return None, None
    doi = doi.strip().lower()
    if doi.startswith("https://doi.org/"):
        doi = doi[len("https://doi.org/"):]
    try:
        r = http_json(f"{ANSA_URL}/api/query", method="POST",
                      body={"type": "paper", "where": {"doi": doi}, "limit": 2})
    except Exception:
        return None, None
    if not r:
        return None, None
    p = r[0]
    return p.get("id"), p.get("properties", {}).get("citekey")


def write_jsonl(records, path=None):
    out = open(path, "w") if path else sys.stdout
    try:
        for rec in records:
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    finally:
        if path:
            out.close()


def shorten(s, n=300):
    if not s:
        return ""
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"


def authors_str(authors_list, max_n=4):
    """Format OpenAlex/S2 author list to 'Lastname, F.; ...' (≤max_n then 'et al.')."""
    if not authors_list:
        return ""
    out = []
    for a in authors_list[:max_n]:
        out.append(a)
    if len(authors_list) > max_n:
        out.append("et al.")
    return "; ".join(out)
