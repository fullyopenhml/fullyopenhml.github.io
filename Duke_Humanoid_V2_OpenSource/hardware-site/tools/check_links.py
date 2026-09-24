"""Check every internal link in the built site — including the ones MkDocs cannot.

``mkdocs build --strict`` validates Markdown links. It does not look inside raw
HTML, so a ``<video src="../../assets/…">`` or the 3D viewer's
``<model-viewer src="…" data-base="…">`` keeps a path that was right at the old
URL depth and silently 404s at the new one. That is exactly what happened when
each section became one flat page and every included file moved up a level.

Checks, over ``site/``:

* every ``href``/``src``/``poster``/``data-base`` that is site-relative resolves
  to a file that exists;
* every ``#fragment`` resolves to an ``id`` on the page it points at.

Usage:  python tools/check_links.py        (after mkdocs build)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
REF = re.compile(r'(?:href|src|poster|data-base)="([^"]*)"')
EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|#|$)", re.I)


def url_prefix() -> str:
    """The path part of ``site_url`` — what a root-absolute link is rooted at.

    Material's 404 page links with ``/duke_humanoid_v2/…`` rather than a
    relative path, because a 404 is served from an unknown depth.
    """
    m = re.search(r"^site_url:\s*\S+?://[^/]+(/\S*?)/?\s*$",
                  (ROOT / "mkdocs.yml").read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else ""


def ids(path: Path, cache: dict[Path, set[str]]) -> set[str]:
    if path not in cache:
        cache[path] = set(re.findall(r'\sid="([^"]+)"',
                                     path.read_text(encoding="utf-8", errors="replace")))
    return cache[path]


def main() -> int:
    if not SITE.is_dir():
        print(f"{SITE} does not exist — run `mkdocs build` first", file=sys.stderr)
        return 1
    prefix = url_prefix()
    cache: dict[Path, set[str]] = {}
    bad: list[str] = []
    for page in sorted(SITE.rglob("*.html")):
        where = page.relative_to(SITE).as_posix()
        for raw in REF.findall(page.read_text(encoding="utf-8", errors="replace")):
            if EXTERNAL.match(raw):
                continue
            target, _, frag = raw.partition("#")
            if not target:                       # same-page anchor
                if frag and frag not in ids(page, cache):
                    bad.append(f"{where}: #{frag} — no such id on this page")
                continue
            if target.startswith("/"):
                if not target.startswith(prefix + "/") and target != prefix:
                    bad.append(f"{where}: {raw} — outside {prefix or '/'}")
                    continue
                resolved = (SITE / target[len(prefix):].lstrip("/")).resolve()
            else:
                resolved = (page.parent / unquote(target)).resolve()
            if resolved.is_dir():
                resolved = resolved / "index.html"
            if not resolved.exists():
                bad.append(f"{where}: {raw} — no such file")
            elif frag and resolved.suffix == ".html" and frag not in ids(resolved, cache):
                bad.append(f"{where}: {raw} — no such id on the target page")

    for line in bad:
        print(f"ERROR: {line}", file=sys.stderr)
    print(f"site/: {len(list(SITE.rglob('*.html')))} pages, {len(bad)} broken links")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
