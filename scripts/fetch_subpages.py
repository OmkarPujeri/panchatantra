#!/usr/bin/env python3
"""Fetch raw wikitext of every subpage of the Wikisource Panchatantra work.

Each story subpage carries <pages index="Panchatantra.djvu" from=N to=M .../> which
gives the exact printed-page range of that story -- that is our boundary source of
truth, since only some stories got named <section> markers.

Writes source/subpages_raw.json
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

API = "https://en.wikisource.org/w/api.php"
ROOT = "The Panchatantra (Purnabhadra's Recension of 1199 CE)"
OUT = os.path.join(os.path.dirname(__file__), "..", "source", "subpages_raw.json")
UA = {"User-Agent": "PanchatantraAI-research/0.1 (educational corpus build)"}


def api(q):
    req = urllib.request.Request(
        API + "?" + urllib.parse.urlencode(q), headers=UA
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def list_subpages():
    titles, cont = [], {}
    while True:
        q = {
            "action": "query", "list": "allpages",
            "apprefix": ROOT + "/", "aplimit": "500",
            "format": "json", "formatversion": "2",
        }
        q.update(cont)
        d = api(q)
        titles += [p["title"] for p in d["query"]["allpages"]]
        if "continue" not in d:
            return titles
        cont = d["continue"]


def fetch_contents(titles):
    out = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i : i + 50]
        d = api({
            "action": "query", "prop": "revisions", "rvprop": "content",
            "rvslots": "main", "titles": "|".join(chunk),
            "format": "json", "formatversion": "2",
        })
        for p in d["query"]["pages"]:
            revs = p.get("revisions")
            out[p["title"]] = revs[0]["slots"]["main"]["content"] if revs else ""
        time.sleep(0.4)
    return out


def main():
    titles = list_subpages()
    print(f"{len(titles)} subpages")
    data = fetch_contents(titles)

    # pull the transclusion range out of each subpage
    for t, wikitext in data.items():
        m = re.search(
            r'<pages\s+index="Panchatantra\.djvu"(.*?)/>', wikitext, re.S
        )
        if not m:
            print(f"  NO TRANSCLUSION: {t}")
            continue
        # attributes may be quoted (fromsection="X") or bare (from=131)
        attrs = {
            k: (q or bare)
            for k, q, bare in re.findall(
                r'(\w+)\s*=\s*(?:"([^"]*)"|([^\s"/]+))', m.group(1)
            )
        }
        data[t] = {"from": attrs.get("from"), "to": attrs.get("to"),
                   "fromsection": attrs.get("fromsection"),
                   "tosection": attrs.get("tosection")}

    json.dump(data, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"wrote {OUT}")
    for t, v in data.items():
        if isinstance(v, dict):
            print(f"  {str(v['from']):>4}-{str(v['to']):<5} {t.split('/')[-1]}")


if __name__ == "__main__":
    main()
