"""Print every red gap mark in the built site with the number gaps.js gives it on the page.

Usage: python tools/list_gaps.py [page ...]     (pages: bom fabrication assembly electrical bringup reference index)
Run `mkdocs build` first. Numbering = page letter + document order, the same rule as docs/javascripts/gaps.js.
"""
import html, re, sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"
LETTER = {"index": "H", "bom": "B", "fabrication": "F", "assembly": "A", "electrical": "E",
          "bringup": "U", "software": "S", "reference": "R"}
MARK = re.compile(r'class="(dh-missing|dh-unverified|pending-figure|admonition missing|admonition unverified)"')

def text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()

def main(pages):
    for page in pages or LETTER:
        path = SITE / ("index.html" if page == "index" else f"{page}/index.html")
        if not path.exists():
            continue
        s = path.read_text(encoding="utf-8")
        a = s[s.find("<article"):s.find("</article>")]
        hits = list(MARK.finditer(a))
        if not hits:
            continue
        print(f"\n== {page}: {len(hits)} ==")
        for n, m in enumerate(hits, 1):
            i = m.start()
            heads = re.findall(r"<h[23][^>]*>(.*?)</h[23]>", a[:i])
            section = text(heads[-1]).replace("¶", "").strip() if heads else "(top)"
            if m.group(1).startswith("admonition"):
                end = a.find("</p>", i)
                ctx = text(a[i:end])
            else:
                tr = a.rfind("<tr>", 0, i)
                if tr > -1 and i - tr < 2500 and a.find("</tr>", i) - tr < 4000:
                    ctx = text(a[tr:a.find("</tr>", i)]).replace("  ", " ")
                else:
                    li = max(a.rfind("<p>", 0, i), a.rfind("<li>", 0, i))
                    ctx = text(a[li:a.find("</", i + 30)]) if li > -1 and i - li < 1500 else text(a[max(0, i - 200):i + 200])
            print(f"  {LETTER[page]}{n:<3d} [{section[:28]}] {ctx[:150]}")

if __name__ == "__main__":
    main(sys.argv[1:])
