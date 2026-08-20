# Zensical Configuration & GitHub Actions CI Template

This document provides the canonical `zensical.toml` and `.github/workflows/docs.yml` configurations for the teaching environment.

---

## 1. `zensical.toml` Template

Replace placeholder variables (`{SITE_NAME}`, `{SITE_DESCRIPTION}`, `{SITE_AUTHOR}`, `{SITE_URL}`, `{TOPIC_SLUG}`, `{YEAR}`) with the actual topic values.

```toml
[project]
site_name = "{SITE_NAME}"
site_description = "{SITE_DESCRIPTION}"
site_author = "{SITE_AUTHOR}"
site_url = "{SITE_URL}"

copyright = """
Copyright &copy; {YEAR} {SITE_AUTHOR}
"""

# Top-level section navigation (Do NOT leak individual lesson files into the sidebar)
nav = [
  { "Home" = "index.md" },
  { "Lessons" = [
     "lessons/index.md"
  ]},
  { "Debugging" = [
     "debugging/index.md"
  ]},
  { "Interview Questions" = [
     "interview/index.md"
  ]},
  { "Cheatsheet" = "cheatsheet/index.md" },
  { "References" = "references/index.md" }
]

[project.theme]
custom_dir = "overrides"
favicon = "assets/{TOPIC_SLUG}-logo.svg"
language = "en"

features = [
  "announce.dismiss",
  "content.action.edit",
  "content.action.view",
  "content.code.annotate",
  "content.code.copy",
  "content.code.select",
  "content.footnote.tooltips",
  "content.tabs.link",
  "content.tooltips",
  "navigation.expand",
  "navigation.footer",
  "navigation.indexes",
  "navigation.instant",
  "navigation.instant.prefetch",
  "navigation.path",
  "navigation.sections",
  "navigation.top",
  "navigation.tracking",
  "search.highlight"
]

[project.theme.icon]
logo = "custom/{TOPIC_SLUG}"

[[project.theme.palette]]
scheme = "default"
toggle.icon = "lucide/sun"
toggle.name = "Switch to dark mode"

[[project.theme.palette]]
scheme = "slate"
toggle.icon = "lucide/moon"
toggle.name = "Switch to light mode"

[[project.extra.social]]
icon = "fontawesome/brands/github"
link = "{SITE_URL}"

# Markdown extensions
[project.markdown_extensions.abbr]
[project.markdown_extensions.admonition]
[project.markdown_extensions.attr_list]
[project.markdown_extensions.def_list]
[project.markdown_extensions.footnotes]
[project.markdown_extensions.md_in_html]
[project.markdown_extensions.toc]
permalink = true

[project.markdown_extensions.pymdownx.arithmatex]
generic = true
[project.markdown_extensions.pymdownx.betterem]
[project.markdown_extensions.pymdownx.caret]
[project.markdown_extensions.pymdownx.details]
[project.markdown_extensions.pymdownx.highlight]
anchor_linenums = true
line_spans = "__span"
pygments_lang_class = true
[project.markdown_extensions.pymdownx.inlinehilite]
[project.markdown_extensions.pymdownx.keys]
[project.markdown_extensions.pymdownx.magiclink]
[project.markdown_extensions.pymdownx.mark]
[project.markdown_extensions.pymdownx.smartsymbols]

[project.markdown_extensions.pymdownx.superfences]
custom_fences = [
  { name = "mermaid", class = "mermaid", format = "pymdownx.superfences.fence_code_format" }
]

[project.markdown_extensions.pymdownx.tabbed]
alternate_style = true
combine_header_slug = true

[project.markdown_extensions.pymdownx.tasklist]
custom_checkbox = true

[project.markdown_extensions.pymdownx.tilde]

[project.markdown_extensions.pymdownx.emoji]
emoji_index = "zensical.extensions.emoji.twemoji"
emoji_generator = "zensical.extensions.emoji.to_svg"
options.custom_icons = ["overrides/.icons"]
```

---

## 2. `.github/workflows/docs.yml` Template

Automated GitHub Actions CI/CD to build and publish the Zensical site to GitHub Pages on pushes to `main` or `master`.

```yaml
name: Documentation

on:
  push:
    branches:
      - master
      - main

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/configure-pages@v6
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v10
        with:
          enable-cache: true
          python-version: "3.14"
      - run: uv run zensical build --clean
      - uses: actions/upload-pages-artifact@v5
        with:
          path: site
      - uses: actions/deploy-pages@v5
        id: deployment
```
