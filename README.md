# Coder Hub

A personal coding profile hub: projects, knowledge notes, and CV — written in Markdown, published as a clean static site.

**Workflow:** edit `content/*.md` → run `python build.py` → preview with `serve.bat` or open `index.html`.

## Repository layout

| Path | Purpose |
|------|---------|
| `content/*.md` | Source of truth — edit these |
| `build.py` | Builds HTML pages from Markdown |
| `index.html`, `projects/`, etc. | Generated site (commit for GitHub Pages) |
| `assets/site.css` | Page styling (MarkView-derived) |
| `serve.bat` | Build + local preview at http://localhost:8000/ |

## Build locally

Requires Python 3:

```powershell
pip install -r requirements.txt
python build.py
```

Double-click **`serve.bat`** to rebuild and open the site in your browser.

After editing Markdown, bump `version` and `date` in the YAML front matter when you want, run `python build.py`, then commit both the `.md` sources and generated `.html` files.

## GitHub Pages (later)

Push the repo with generated HTML at the root. No CI build step — regenerate locally before pushing, same as [ghidra-reags-quickstart](https://github.com/selloa/ghidra-reags-quickstart).

Relative links work whether you use a **user site** (`selloa.github.io`) or a **project site** (`selloa.github.io/coder-hub/`).

## Adding content

- **Projects:** edit `content/projects.md` — link to separate tutorial repos (e.g. Ghidra quickstart) or add new pages to the manifest in `build.py` later.
- **Knowledge:** edit `content/knowledge.md` — topic sections as `##` headings.
- **CV:** edit `content/cv.md`.

## Status

Initial scaffold (v0.1.0). Grow incrementally.
