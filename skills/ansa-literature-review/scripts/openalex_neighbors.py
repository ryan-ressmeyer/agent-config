#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
openalex_neighbors.py — references / cited-by walks via OpenAlex, deduped against ansa.

USAGE
  ./openalex_neighbors.py --doi 10.1038/371511a0 --mode references
  ./openalex_neighbors.py --doi 10.1038/371511a0 --mode cited-by --limit 100
  ./openalex_neighbors.py --doi ... --mode both --new-only -o neighbors.jsonl

Either --doi or --openalex-id is accepted. --mode both runs references then cited-by
and tags each record with a `relation` field.
"""
import argparse
import sys
import urllib.parse
from _common import http_json, ansa_lookup_doi, write_jsonl, shorten, CONTACT_EMAIL


def reconstruct_abstract(inv_idx):
    if not inv_idx:
        return ""
    pos = [(i, w) for w, idxs in inv_idx.items() for i in idxs]
    pos.sort()
    return " ".join(w for _, w in pos)


def fetch_work(seed):
    """seed may be a DOI or an OpenAlex work id (W...)."""
    if seed.startswith("W") and seed[1:].isdigit():
        url = f"https://api.openalex.org/works/{seed}?mailto={CONTACT_EMAIL}"
    else:
        doi = seed.replace("https://doi.org/", "")
        url = f"https://api.openalex.org/works/https://doi.org/{doi}?mailto={CONTACT_EMAIL}"
    return http_json(url)


def normalize(w):
    doi = (w.get("doi") or "").replace("https://doi.org/", "")
    authors = [a.get("author", {}).get("display_name", "")
               for a in (w.get("authorships") or [])
               if a.get("author", {}).get("display_name")]
    host = (w.get("host_venue") or {}) or ((w.get("primary_location") or {}).get("source") or {})
    journal = host.get("display_name", "") if isinstance(host, dict) else ""
    abstract = reconstruct_abstract(w.get("abstract_inverted_index"))
    return {
        "doi": doi or None,
        "openalex_id": w.get("id", "").replace("https://openalex.org/", ""),
        "title": w.get("display_name") or w.get("title") or "",
        "year": w.get("publication_year"),
        "journal": journal,
        "authors": authors,
        "citation_count": w.get("cited_by_count"),
        "abstract": shorten(abstract, 600),
    }


def get_references(seed_work, limit):
    refs = seed_work.get("referenced_works") or []
    out = []
    for oid in refs[:limit]:
        oid_short = oid.replace("https://openalex.org/", "")
        try:
            w = http_json(f"https://api.openalex.org/works/{oid_short}?mailto={CONTACT_EMAIL}")
            out.append(w)
        except Exception as e:
            print(f"  [refs] skip {oid_short}: {e}", file=sys.stderr)
    return out


def get_cited_by(seed_work, limit):
    seed_id = seed_work.get("id", "").replace("https://openalex.org/", "")
    params = {
        "filter": f"cites:{seed_id}",
        "per-page": str(min(limit, 200)),
        "sort": "cited_by_count:desc",
        "mailto": CONTACT_EMAIL,
    }
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    data = http_json(url)
    return (data.get("results") or [])[:limit]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--doi")
    src.add_argument("--openalex-id")
    ap.add_argument("--mode", choices=["references", "cited-by", "both"], default="both")
    ap.add_argument("--limit", type=int, default=50, help="cap per direction")
    ap.add_argument("--new-only", action="store_true")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()

    seed_key = args.doi or args.openalex_id
    print(f"[openalex] fetching seed work {seed_key}", file=sys.stderr)
    seed = fetch_work(seed_key)
    seed_title = seed.get("display_name", "")
    print(f"[openalex] seed: {seed_title[:80]}", file=sys.stderr)

    records = []
    if args.mode in ("references", "both"):
        print(f"[openalex] pulling references (limit {args.limit})", file=sys.stderr)
        for w in get_references(seed, args.limit):
            rec = normalize(w); rec["relation"] = "reference"
            records.append(rec)
    if args.mode in ("cited-by", "both"):
        print(f"[openalex] pulling cited-by (limit {args.limit})", file=sys.stderr)
        for w in get_cited_by(seed, args.limit):
            rec = normalize(w); rec["relation"] = "cited-by"
            records.append(rec)

    seen_dois = set()
    final = []
    for rec in records:
        if rec["doi"] and rec["doi"] in seen_dois:
            continue
        if rec["doi"]:
            seen_dois.add(rec["doi"])
        aid, ck = ansa_lookup_doi(rec["doi"]) if rec["doi"] else (None, None)
        rec["in_graph"] = aid is not None
        rec["ansa_id"] = aid
        rec["ansa_citekey"] = ck
        if args.new_only and rec["in_graph"]:
            continue
        final.append(rec)
    in_g = sum(1 for r in final if r["in_graph"])
    print(f"[openalex] {len(final)} records ({in_g} already in graph)", file=sys.stderr)
    write_jsonl(final, args.output)


if __name__ == "__main__":
    main()
