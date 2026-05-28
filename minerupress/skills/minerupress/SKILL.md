---
name: minerupress
description: 'Use when an AI agent needs to help a user or contributor work with MineruPress: install the released CLI, initialize a book workspace, choose exactly one source mode (`uploaded_result`, `official_api`, or `local_toolchain`), export MinerU results into MkDocs Material chapters, inspect heading boundaries, verify builds, troubleshoot generated output, develop plugins, or maintain the MineruPress repository. Trigger for MineruPress, minerupress, MinerU content_list.json, book.yml, `minerupress init`, `minerupress export`, `minerupress fetch`, `minerupress headings`, `minerupress fingerprint`, generated docs/chapters, or PDF-to-MkDocs book publishing automation.'
---

# MineruPress

Use this skill to support MineruPress as a user-facing publishing tool and as a contributor-maintained Python package.

## Audience Split

For ordinary users, prefer the released package and an isolated book workspace:

```bash
pip install "minerupress[all]"
pip install mkdocs mkdocs-material
minerupress init my-book
cd my-book
```

For contributors changing MineruPress itself, use the repository checkout:

```bash
git clone https://github.com/aronnaxlin/minerupress.git
cd minerupress
pip install -e ".[dev]"
```

Do not make users clone the toolchain repo just to run a book. The bundled template is copied with `minerupress init <directory>` from the installed package.

## Source Modes

Choose exactly one source mode per book workspace:

- `uploaded_result`: The user already has MinerU output under `resources/mineru/`. This is the bundled template default and has no network or local parsing side effects.
- `official_api`: The user starts from PDFs and wants MinerU official API parsing. Requires `api.sources` and `MINERU_API_TOKEN`.
- `local_toolchain`: The user starts from PDFs, images, Office files, or a directory and already installed MinerU's `mineru` CLI separately.

MineruPress must not bundle MinerU or silently install it. For `local_toolchain`, point users to MinerU official installation and CLI docs, with `uv pip install -U "mineru[all]"` as the common install path and official docs as the authority for optional backends and parameters.

## Preferred User Workflow

1. Create or enter an isolated book workspace with `minerupress init <dir>`.
2. Choose one `source` in `book.yml`.
3. Prepare source data:
   - For `uploaded_result`, put MinerU output directories under `resources/mineru/`.
   - For `official_api`, put PDFs under `resources/pdfs/`, configure `api.sources`, then run `minerupress fetch book.yml`.
   - For `local_toolchain`, install MinerU separately, configure `local_toolchain.sources`, then run `minerupress fetch book.yml`.
4. Inspect generated MinerU output and heading candidates.
5. Refine `chapters` in `book.yml`.
6. Run `minerupress export book.yml`.
7. Verify with `mkdocs build --strict`.
8. Optionally create fingerprints with `minerupress fingerprint --docs-dir docs --out reports/fingerprints.json`.

Use `minerupress export --fetch book.yml` only as a convenience or backward-compatible shortcut. In explanations, keep `fetch` as "prepare source then export" and `export` as "export existing MinerU output".

## Workspace Rules

When operating on a book workspace:

- Read `book.yml` and `mkdocs.yml` first.
- Read local `AGENTS.md` if present.
- Treat `.env`, source PDFs, `resources/mineru/`, `docs/chapters/`, `docs/images/`, `site/`, and `reports/` as local/generated unless the user explicitly wants to version that book project.
- Do not hand-edit generated chapter Markdown as the durable fix; update `book.yml`, the source MinerU output, or a plugin.
- Copy PDFs into the workspace, usually under `resources/pdfs/`, before API fetch or local parsing. This avoids PDF splitting into protected/cloud-drive paths.

## Commands

Current primary CLI:

```bash
minerupress init my-book
minerupress export book.yml
minerupress fetch book.yml
minerupress headings resources/mineru --volume-uid my-book --format yaml --body-only
minerupress fingerprint --docs-dir docs --out reports/fingerprints.json
```

Legacy wrappers such as `minerupress-export`, `minerupress-fetch`, `minerupress-headings`, `mineru-export`, and `mineru-fetch` remain available only for existing projects. Do not present them as the main workflow.

## `book.yml` Guidance

Set `source` explicitly for new configs:

```yaml
source: uploaded_result
mineru_root: resources/mineru
docs_out: docs
volume_uid: my-book
toc_max_page: 10
allow_missing_boundaries: false

plugins:
  - qr_filter
  - cjk_spacing

chapters:
  - slug: ch01-overview
    title: 第1章 概述
```

For API mode:

```yaml
source: official_api
api:
  token: ""
  enable_formula: true
  enable_table: true
  model_version: vlm
  sources:
    my-book: resources/pdfs/book.pdf
```

For local MinerU CLI mode:

```yaml
source: local_toolchain
local_toolchain:
  executable: mineru
  args:
    - -b
    - pipeline
  sources:
    my-book: resources/pdfs/book.pdf
```

`local_toolchain.args` must not include `-p`, `--path`, `-o`, or `--output`; MineruPress appends those automatically.

## Chapter Boundary Guidance

Prefer chapter `title` plus `slug`; omit regexes unless matching is ambiguous.

Use `aliases` for alternate visible headings:

```yaml
chapters:
  - slug: appendix-a
    title: 附录A 部分习题的解答
    aliases:
      - Appendix A
```

Use `start_patterns` for precise regex alternatives:

```yaml
chapters:
  - slug: unit-01
    title: 第一单元 Web 基础
    start_patterns:
      - "^Unit\\s*1\\b"
      - "^第\\s*一\\s*单元"
```

Only use `--allow-missing-boundaries` while diagnosing bad MinerU output. A successful production run should find every configured chapter boundary.

If TOC lines such as `第1章 引论 …… 3` are matched before the real body heading, switch to exact body-heading regexes:

```yaml
chapters:
  - slug: ch01-introduction
    title: 引论
    start_pattern: "^第\\s*1\\s*章$"
```

Use the headings helper before hand-writing many boundaries:

```bash
minerupress headings resources/mineru --volume-uid my-book --format report
minerupress headings resources/mineru --volume-uid my-book --format yaml --body-only
```

## Verification

For a user workspace:

```bash
minerupress export book.yml
mkdocs build --strict
```

For repository development:

```bash
python -m compileall minerupress
pytest
```

When template behavior changes, confirm `book_template/` and `minerupress/book_template/` are synchronized and that `minerupress init <tmp-dir>` creates a buildable placeholder site.

## Generated Output Behavior

Each export rebuilds:

- `docs/chapters/`
- `docs/images/`

If a chapter appears wrong, fix the configuration, source data, or plugin. Avoid treating generated Markdown as the source of truth.

## Content Details

MinerU code items may store their body in `code_body` rather than `text`. The exporter preserves already-fenced code blocks from MinerU and wraps unfenced code.

Literal HTML/XML tags in normal prose and captions are escaped during export so textbooks can discuss tags such as `<span>` without MkDocs rendering them as real HTML. Raw `table_body` HTML is preserved as table markup.

## References

Read `references/book-yml.md` for compact config examples. For the current end-to-end user workflow, read `docs/guide/getting-started.md`, `docs/guide/configuration.md`, and `docs/guide/workflow-run-a-book.md`.

## Practical Lessons (Real-World Experience)

These are hard-won learnings from actual user sessions that the abstract documentation does not capture.

### toc_max_page Off-by-One

`toc_max_page` filters items whose `page_idx < threshold`. In a typical course-PDF (title slide → TOC → body), page indices are:

- `page_idx=0`: title slide (封面)
- `page_idx=1`: TOC (目录)
- `page_idx=2`: first body page (第一页正文)

If `toc_max_page` is set to `3`, body content starting on `page_idx=2` is **silently skipped** and the first chapter boundary is never found, even when the `start_pattern` would match. The chapter is then skipped under `allow_missing_boundaries: True`, producing an almost-empty file (often just the chapter title from `book.yml`).

**Fix**: set `toc_max_page: 2` for PDFs where the body starts on the third physical page. Or `toc_max_page: 0` to disable filtering entirely when unsure.

### start_pattern: Prefer Simplicity

Chinese part/section headings in MinerU output may have unpredictable punctuation, whitespace, or trailing annotation. For example, the actual text might be `图像从哪里来：图像形成与数字图像基础` while the pattern expects `图像从哪里来` with anchors.

Avoid over-specifying patterns:

```yaml
# Good — works with or without trailing text
start_pattern: 第二部分

# Fragile — breaks if actual text is "第二部分：图像增强与滤波"
start_pattern: 第二部分.*图像增强与滤波
```

The MineruPress auto-generated patterns from `title` are also helpful. A title like `第一部分 图像形成与数字图像基础` auto-generates patterns that match `第一部分...` headings, but not `图像从哪里来：...` headings. If the actual PDF section heading differs from the book.yml title, supply a `start_pattern`.

### List Items Silent Drop

MinerU v1 `content_list.json` stores list content in the `list_items` field (a list of strings like `["- item one", "- item two"]`), **not** in the `text` field. The `_item_to_md()` function in `minerupress/core.py` originally read only `item.get("text", "")`:

```python
text = item.get("text", "").strip()
if not text:
    return None  # ← list items silently dropped here (109 items in a typical 81-page PDF)
```

**Fix**: Add a `list` type handler before the text fallback:

```python
if t == "list":
    items = item.get("list_items")
    if items and isinstance(items, list):
        lines = "\n".join(str(li).strip() for li in items if str(li).strip())
        if lines:
            return _apply_text_plugins(item, lines, plugins)
    return None
```

This is the single most impactful fix for content-completeness — list items account for ~15% of all items in a typical course-PDF.

### Homepage Is a Template Placeholder

`minerupress init` generates a generic `docs/index.md` with placeholder text. For a course PDF, replace it with the title slide information (course name, instructor, schedule, department, email) and a table-of-contents overview derived from the PDF structure.

### Editable Install Caveat

When `minerupress` is installed via `pip install -e ...` (editable mode), changes to `minerupress/core.py` take effect **immediately** without re-installation. The modified file is used directly from the source tree.

### Heading Hierarchy: Per-Page First Headings

MinerU v1 `content_list.json` assigns `text_level: 1` to nearly all text headings (307 out of 491 text items in a typical 81-page course PDF). If every heading is rendered as `#`, the MkDocs Table of Contents sidebar becomes a flat, useless list.

The exporter in `minerupress/core.py` handles this with **page-aware heading demotion** (added in the main export loop, not in `_item_to_md`):

1. The first `#` line is always the chapter title from `book.yml`.
2. For each subsequent heading item, track its `page_idx`.
3. The **first** heading item on each PDF page → rendered as `##` (shows in MkDocs right-side TOC).
4. All **subsequent** heading items on the same page → rendered as **plain text** (no `#` prefix), keeping the content visible but not polluting the TOC.

Key implementation detail — initialize `seen_chapter_title = True` before the item loop because line[0] is already the chapter title:

```python
lines: list[str] = [f"# {ch.title}", ""]
seen_chapter_title = True
last_page_idx: int | None = None
first_on_page = True
for item_idx, item, segment in chapter_items:
    md = _item_to_md(item, ...)
    if md and md.lstrip().startswith("# "):
        if not seen_chapter_title:
            seen_chapter_title = True       # first heading = chapter title
        else:
            pg = item.get("page_idx")
            if pg is not None and pg != last_page_idx:
                last_page_idx = pg
                first_on_page = True
            if first_on_page:
                md = f"## {stripped[2:]}"   # first on page → level-2
                first_on_page = False
            else:
                md = stripped[2:]           # subsequent → plain text
    lines.append(md)
    lines.append("")
```

Without this logic, a typical 5-chapter PDF produces 60+ flat `#` headings. With it, only 1 `#` + ~19 `##` per chapter (one per body page).

### Default Theme

MkDocs Material's `theme.palette.primary` only accepts a fixed set of named colors. **Default to `light-blue`** — do not add custom CSS overrides for the primary color.

```yaml
theme:
  palette:
    primary: light-blue
    accent: light-blue
```

### Git Submodule Deploy Trap

The `minerupress/` directory inside the book workspace is often a standalone git repository (it has its own `.git/`). When the parent book workspace is pushed to a remote for Cloudflare Pages deployment, git records it as a submodule entry (mode `160000`). Cloudflare's `git clone` then tries to init submodules but fails because no `.gitmodules` file exists.

**Fix**: Before committing the parent workspace:

```bash
rm -rf minerupress/.git
git rm --cached minerupress       # remove the submodule entry
git add minerupress/               # re-add as regular files
```

Or configure Cloudflare Pages to **not** initialize submodules (set `CF_PAGES_SUBMODULES=false` in environment variables).

