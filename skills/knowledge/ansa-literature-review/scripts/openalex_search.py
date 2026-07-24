#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
openalex_search.py — topic search via OpenAlex, deduped against ansa.

USAGE
  ./openalex_search.py "saccadic suppression magnocellular LGN"
  ./openalex_search.py "saccadic suppression LGN" --year-min 1990 --per-page 50 --pages 2
  ./openalex_search.py "..." --new-only          # drop in_graph hits
  ./openalex_search.py "..." -o candidates.jsonl

OUTPUT
  JSON Lines, one paper per line:
    {doi, openalex_id, title, year, journal, authors, citation_count,
     abstract, in_graph, ansa_id, ansa_citekey}
"""
import argparse
import sys
import urllib.parse
from _common import http_json, ansa_lookup_doi, write_jsonl, shorten, authors_str, CONTACT_EMAIL


def reconstruct_abstract(inv_idx):
    if not inv_idx:
        return ""
    pos = []
    for word, idxs in inv_idx.items():
        for i in idxs:
            pos.append((i, word))
    pos.sort()
    return " ".join(w for _, w in pos)


def normalize_work(w):
    doi = (w.get("doi") or "").replace("https://doi.org/", "")
    authors = [a.get("author", {}).get("display_name", "")
               for a in (w.get("authorships") or [])
               if a.get("author", {}).get("display_name")]
    journal = ""
    host = (w.get("host_venue") or {}) or (w.get("primary_location") or {}).get("source") or {}
    if isinstance(host, dict):
        journal = host.get("display_name", "") or ""
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", help="search string")
    ap.add_argument("--per-page", type=int, default=25)
    ap.add_argument("--pages", type=int, default=1, help="number of result pages to pull")
    ap.add_argument("--year-min", type=int, default=None)
    ap.add_argument("--year-max", type=int, default=None)
    ap.add_argument("--new-only", action="store_true", help="omit papers already in ansa")
    ap.add_argument("-o", "--output", default=None, help="JSONL output file (default: stdout)")
    args = ap.parse_args()

    params = {
        "search": args.query,
        "per-page": str(args.per_page),
        "mailto": CONTACT_EMAIL,
    }
    filters = []
    if args.year_min:
        filters.append(f"from_publication_date:{args.year_min}-01-01")
    if args.year_max:
        filters.append(f"to_publication_date:{args.year_max}-12-31")
    if filters:
        params["filter"] = ",".join(filters)

    records = []
    for page in range(1, args.pages + 1):
        params["page"] = str(page)
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        print(f"[openalex] page {page}: {url}", file=sys.stderr)
        data = http_json(url)
        works = data.get("results") or []
        if not works:
            break
        for w in works:
            rec = normalize_work(w)
            aid, ck = ansa_lookup_doi(rec["doi"]) if rec["doi"] else (None, None)
            rec["in_graph"] = aid is not None
            rec["ansa_id"] = aid
            rec["ansa_citekey"] = ck
            if args.new_only and rec["in_graph"]:
                continue
            records.append(rec)
    print(f"[openalex] {len(records)} records ({sum(1 for r in records if r['in_graph'])} already in graph)",
          file=sys.stderr)
    write_jsonl(records, args.output)


if __name__ == "__main__":
    main()
