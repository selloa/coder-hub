#!/usr/bin/env python3
"""Build static HTML pages from content/*.md (source of truth)."""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import markdown
from markdown.extensions.toc import TocExtension

ROOT = Path(__file__).resolve().parent
STYLESHEET = ROOT / "assets" / "site.css"

PAGES: list[tuple[str, str, str]] = [
    ("content/index.md", "index.html", "home"),
    ("content/projects.md", "projects/index.html", "projects"),
    ("content/knowledge.md", "knowledge/index.html", "knowledge"),
    ("content/cv.md", "cv/index.html", "cv"),
]

NAV_ITEMS = [
    ("home", "Home", "index.html"),
    ("projects", "Projects", "projects/index.html"),
    ("knowledge", "Knowledge", "knowledge/index.html"),
    ("cv", "CV", "cv/index.html"),
]

INTERNAL_SECTION = re.compile(r"^## Page build notes\b", re.MULTILINE)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FRONT_MATTER = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
PRE_BLOCK = re.compile(r"<pre>(.*?)</pre>", re.DOTALL)
H2_HEADING = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.DOTALL)


def slugify(value: str, separator: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", separator, value)


def path_prefix(output_path: str) -> str:
    depth = len(Path(output_path).parent.parts)
    return "../" * depth if depth else ""


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = FRONT_MATTER.match(text)
    if not match:
        return {}, text

    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, text[match.end() :]


def strip_internal_sections(text: str) -> str:
    match = INTERNAL_SECTION.search(text)
    if match:
        text = text[: match.start()].rstrip()
    return HTML_COMMENT.sub("", text).strip() + "\n"


def postprocess_body(html: str) -> str:
    html = PRE_BLOCK.sub(
        r'<div class="markview-code-block-wrapper"><pre>\1</pre></div>',
        html,
    )
    html = html.replace("<img ", '<img loading="lazy" ')
    html = re.sub(
        r'<input type="checkbox"\s+disabled\s*/?>',
        "<input type=\"checkbox\">",
        html,
    )
    return html


def extract_sidebar_nav(body_html: str) -> str:
    items = []
    for slug, raw_title in H2_HEADING.findall(body_html):
        title = re.sub(r"<[^>]+>", "", raw_title).strip()
        items.append(f'        <li><a href="#{slug}">{title}</a></li>')
    if not items:
        return ""
    links = "\n".join(items)
    return f"""  <aside class="site-sidebar" id="site-sidebar" aria-label="Page sections">
    <div class="site-sidebar-header">
      <p class="site-sidebar-title">On this page</p>
      <button type="button" class="site-sidebar-toggle" id="sidebar-hide" aria-controls="site-sidebar" aria-expanded="true" title="Hide navigation">Hide</button>
    </div>
    <nav>
      <ul>
{links}
      </ul>
    </nav>
  </aside>"""


def build_topnav(prefix: str, current: str) -> str:
    links = []
    for page_id, label, href in NAV_ITEMS:
        current_attr = ' aria-current="page"' if page_id == current else ""
        links.append(
            f'      <li><a href="{prefix}{href}"{current_attr}>{label}</a></li>'
        )
    joined = "\n".join(links)
    return f"""    <nav class="site-topnav" aria-label="Site">
      <ul>
{joined}
      </ul>
    </nav>"""


def render_markdown(content: str) -> str:
    return markdown.markdown(
        content,
        extensions=[
            TocExtension(slugify=slugify, separator="-", toc_depth=6),
            "markdown.extensions.tables",
            "markdown.extensions.fenced_code",
            "markdown.extensions.sane_lists",
            "markdown.extensions.nl2br",
            "pymdownx.tasklist",
        ],
        extension_configs={
            "pymdownx.tasklist": {
                "custom_checkbox": False,
            },
        },
        output_format="html5",
    )


def build_html(
    meta: dict[str, str],
    body_html: str,
    sidebar_nav: str,
    *,
    source_name: str,
    output_path: str,
    page_id: str,
) -> str:
    title = meta.get("title", "Coder Hub")
    version = meta.get("version", "0.0.0")
    date = meta.get("date", "")
    status = meta.get("status", "draft")
    description = meta.get(
        "description",
        "Personal coding hub — projects, knowledge, and CV.",
    )

    prefix = path_prefix(output_path)
    topnav = build_topnav(prefix, page_id)
    sidebar_key = f"coder-hub-sidebar-hidden-{page_id}"

    indented = "\n".join(
        f"    {line}" if line.strip() else line for line in body_html.splitlines()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="dark">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg">
  <link rel="stylesheet" href="{prefix}assets/site.css">
</head>
<body class="markdown-export" data-theme="dark">
  <header class="site-header">
    <div class="wrap">
      <h1>{title}</h1>
      <p class="meta">Version {version} · {date} · {status} · by <a href="https://github.com/selloa">selloa</a></p>
{topnav}
    </div>
  </header>
  <div class="site-layout">
    <button type="button" class="site-sidebar-show" id="sidebar-show" hidden aria-controls="site-sidebar" title="Show navigation">Show nav</button>
{sidebar_nav}
    <main id="markview-container" class="markdown-body code-block-scroll">
{indented}
    </main>
  </div>
  <footer class="site-footer">
    <p>Built from <code>{source_name}</code> · v{version} · {date} · <a href="https://github.com/selloa">selloa</a></p>
  </footer>
  <a href="#" class="back-top" id="backTop" aria-label="Back to top">↑ Top</a>
  <script>
  (function () {{
    var hideBtn = document.getElementById('sidebar-hide');
    var showBtn = document.getElementById('sidebar-show');
    var storageKey = '{sidebar_key}';

    function setSidebarHidden(hidden) {{
      document.body.classList.toggle('sidebar-hidden', hidden);
      if (hideBtn) hideBtn.setAttribute('aria-expanded', hidden ? 'false' : 'true');
      if (showBtn) showBtn.hidden = !hidden;
      try {{ localStorage.setItem(storageKey, hidden ? '1' : '0'); }} catch (e) {{}}
    }}

    try {{
      if (localStorage.getItem(storageKey) === '1') setSidebarHidden(true);
    }} catch (e) {{}}

    if (hideBtn) hideBtn.addEventListener('click', function () {{ setSidebarHidden(true); }});
    if (showBtn) showBtn.addEventListener('click', function () {{ setSidebarHidden(false); }});

    var backTop = document.getElementById('backTop');
    if (backTop) {{
      window.addEventListener('scroll', function () {{
        backTop.classList.toggle('visible', window.scrollY > 400);
      }});
      backTop.addEventListener('click', function (e) {{
        e.preventDefault();
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }});
    }}
  }})();
  </script>
</body>
</html>
"""


def build_page(source_rel: str, output_rel: str, page_id: str) -> bool:
    source = ROOT / source_rel
    output = ROOT / output_rel

    if not source.exists():
        print(f"Error: source file not found: {source}", file=sys.stderr)
        return False

    raw = source.read_text(encoding="utf-8")
    meta, content = parse_front_matter(raw)
    content = strip_internal_sections(content)

    body_html = postprocess_body(render_markdown(content))
    sidebar_nav = extract_sidebar_nav(body_html)
    html = build_html(
        meta,
        body_html,
        sidebar_nav,
        source_name=source_rel,
        output_path=output_rel,
        page_id=page_id,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8", newline="\n")
    print(f"Wrote {output.relative_to(ROOT)} (from {source.name}, v{meta.get('version', '?')})")
    return True


def main() -> int:
    if not STYLESHEET.exists():
        print(f"Error: stylesheet not found: {STYLESHEET}", file=sys.stderr)
        return 1

    ok = True
    for source_rel, output_rel, page_id in PAGES:
        if not build_page(source_rel, output_rel, page_id):
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
