#!/usr/bin/env python3
"""Crawl the locally served site and verify it (Python 3 standard library only).

Usage:  python3 -m http.server 8000   # in one terminal
        python3 check_site.py         # in another (optional arg: base URL)

Checks: every page loads, internal links/assets/anchors resolve, one title/description/canonical per page,
JSON-LD parses, no placeholder text, hreflang reciprocity, robots.txt and sitemap.xml.
"""
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.dom.minidom
from html.parser import HTMLParser

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/") + "/"
BAD = ("platzhalter", "musterstraße", "000000", "example.com", "todo")
errors = []


def fail(msg):
    errors.append(msg)
    print("FAIL", msg)


def fetch(url):
    try:
        with urllib.request.urlopen(url) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.titles, self.meta_desc, self.canon = [], set(), 0, 0, []
        self.alt, self.jsonld, self._ld = {}, [], False

    def handle_starttag(self, tag, a):
        a = dict(a)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ("img", "script") and a.get("src"):
            self.links.append(a["src"])
        if tag == "link" and a.get("href") and a.get("rel") in ("stylesheet", "icon"):
            self.links.append(a["href"])
        if tag == "link" and a.get("rel") == "canonical":
            self.canon.append(a["href"])
        if tag == "link" and a.get("rel") == "alternate" and a.get("hreflang"):
            self.alt[a["hreflang"]] = a["href"]
        if tag == "title":
            self.titles += 1
        if tag == "meta" and a.get("name") == "description":
            self.meta_desc += 1
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld = True
            self.jsonld.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self._ld = False

    def handle_data(self, data):
        if self._ld:
            self.jsonld[-1] += data


def main():
    status, sm = fetch(BASE + "sitemap.xml")
    if status != 200:
        fail("sitemap.xml not reachable")
        return
    xml.dom.minidom.parseString(sm)
    sm_urls = re.findall(r"<loc>([^<]+)</loc>", sm)
    host = re.match(r"https?://[^/]+", sm_urls[0]).group(0)  # e.g. https://DOMAIN
    to_local = lambda u: BASE + u[len(host) + 1:]
    status, robots = fetch(BASE + "robots.txt")
    if status != 200 or "Sitemap:" not in robots or "Disallow: /" in robots:
        fail("robots.txt missing/blocking or has no Sitemap line")
    for bot in ("GPTBot", "Google-Extended", "PerplexityBot", "ClaudeBot"):
        if bot.lower() in robots.lower() and "disallow" in robots.lower():
            fail(f"robots.txt mentions {bot}")

    seen, queue, pages = set(), [BASE] + [to_local(u) for u in sm_urls], {}
    while queue:
        url = queue.pop(0).split("#")[0]
        if url in seen:
            continue
        seen.add(url)
        status, body = fetch(url)
        if status != 200:
            fail(f"{url} -> HTTP {status}")
            continue
        if not url.endswith((".html", "/")):
            continue  # asset
        p = P()
        p.feed(body)
        pages[url] = (p, body)
        for h in p.links:
            if h.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            queue.append(urllib.parse.urljoin(url, h))
    print(f"crawled {len(seen)} URLs, {len(pages)} HTML pages")

    for url, (p, body) in pages.items():
        name = url[len(BASE):] or "/"
        if p.titles != 1 or p.meta_desc != 1 or len(p.canon) != 1:
            fail(f"{name}: title={p.titles} description={p.meta_desc} canonical={len(p.canon)} (each must be 1)")
        for raw in p.jsonld:
            try:
                json.loads(raw)
            except ValueError as e:
                fail(f"{name}: JSON-LD does not parse: {e}")
        text = re.sub(r"<script[^>]*>.*?</script>", "", body, flags=re.S).lower()
        for b in BAD:
            if b in text or b in "".join(p.jsonld).lower():
                fail(f"{name}: contains '{b}'")
        for h in p.links:  # anchors on the same page
            if h.startswith("#") and len(h) > 1 and h[1:] not in p.ids:
                fail(f"{name}: broken anchor {h}")
        for h in p.links:  # anchors on other pages
            if "#" in h and not h.startswith(("#", "http", "mailto", "tel")):
                tgt, frag = urllib.parse.urljoin(url, h).split("#")
                if frag and tgt in pages and frag not in pages[tgt][0].ids:
                    fail(f"{name}: broken anchor {h}")
        # hreflang: self + reciprocal
        if p.alt:
            me = host + "/" + url[len(BASE):]
            if p.canon and p.canon[0] != me:
                fail(f"{name}: canonical {p.canon[0]} != {me}")
            if me not in p.alt.values():
                fail(f"{name}: hreflang has no self reference")
            for lang, href in p.alt.items():
                other = pages.get(to_local(href))
                if not other or other[0].alt != p.alt:
                    fail(f"{name}: hreflang {lang} -> {href} not reciprocal/missing")
    for u in sm_urls:
        if to_local(u) not in pages:
            fail(f"sitemap URL not crawled: {u}")
    print("\nRESULT:", "FAILED" if errors else "ALL CHECKS PASSED")
    sys.exit(1 if errors else 0)


main()
