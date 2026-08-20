---
name: setup-teaching-site
description: Scaffold a Zensical teaching workspace with the /teach skill.
disable-model-invocation: true
argument-hint: "<topic> [site_name] [site_url]"
---

# Setup Teaching Site

Scaffold an interactive [Zensical](https://zensical.org) teaching workspace configured with the `/teach` skill, curriculum modules, visual Mermaid diagrams, and GitHub Pages deployment.

## Execution Sequence

Execute these steps in order. Each step ends on a completion criterion that must be satisfied before proceeding.

### Step 1: Collect Inputs & Initialize Python Project

1. Resolve parameters from user arguments or prompt if missing:
   - **Topic**: e.g., `Kubernetes`, `Rust`, `Kafka`, `Spring Boot`
   - **Site Name**: e.g., `Learn Kubernetes Architecture`
   - **Author / GitHub Handle**: e.g., `rohit1024`
   - **Site URL**: e.g., `https://<github-handle>.github.io/<repo-name>`
2. Initialize project with `uv`:
   ```bash
   uv init --no-pin-python --python ">=3.14" .
   uv add --dev "zensical>=0.0.55"
   ```
3. Create `.gitignore`:
   ```gitignore
   .venv/
   site/
   .cache/
   __pycache__/
   *.pyc
   .DS_Store
   ```

> **Completion Criterion**: `pyproject.toml` lists `zensical` in `dev` dependencies, `.venv` exists, and `uv run zensical --version` exits 0.

---

### Step 2: Retrieve Branding & SVG Logo

Fetch the topic's SVG logo from [SVGL](https://svgl.app) or generate a clean SVG badge per [SVGL-INTEGRATION.md](SVGL-INTEGRATION.md):

1. Create target directories:
   ```bash
   mkdir -p overrides/.icons/custom overrides/.icons/svgl docs/assets
   ```
2. Download the logo (e.g. `SLUG="kubernetes"`):
   ```bash
   curl -sSL "https://raw.githubusercontent.com/pheralb/svgl/main/static/library/${SLUG}.svg" -o "overrides/.icons/custom/${SLUG}.svg"
   cp "overrides/.icons/custom/${SLUG}.svg" "overrides/.icons/svgl/${SLUG}.svg"
   cp "overrides/.icons/custom/${SLUG}.svg" "docs/assets/${SLUG}-logo.svg"
   ```
3. Fallback: If download fails or offline, generate a clean high-contrast SVG badge matching the format in [SVGL-INTEGRATION.md](SVGL-INTEGRATION.md).

> **Completion Criterion**: `overrides/.icons/custom/<slug>.svg` and `docs/assets/<slug>-logo.svg` exist and contain valid `<svg>` XML markup.

---

### Step 3: Configure `zensical.toml` & GitHub Actions CI

1. Write `zensical.toml` at the project root using [ZENSICAL-CONFIG-TEMPLATE.md](ZENSICAL-CONFIG-TEMPLATE.md):
   - Substitute `{SITE_NAME}`, `{SITE_DESCRIPTION}`, `{SITE_AUTHOR}`, `{SITE_URL}`, `{TOPIC_SLUG}`, and `{YEAR}`.
   - Maintain top-level section roots in `nav` (never add individual lessons to `nav`).
2. Write `.github/workflows/docs.yml` using the workflow template in [ZENSICAL-CONFIG-TEMPLATE.md](ZENSICAL-CONFIG-TEMPLATE.md).

> **Completion Criterion**: `zensical.toml` and `.github/workflows/docs.yml` exist with all topic variables substituted.

---

### Step 4: Scaffold Documentation Portal Hierarchy

Create the documentation files using the templates in [CURRICULUM-TEMPLATES.md](CURRICULUM-TEMPLATES.md), populating all content with `<topic>`-specific modules, lessons, and Mermaid diagrams:

```text
docs/
├── assets/<topic-slug>-logo.svg
├── cheatsheet/index.md
├── debugging/index.md
├── interview/index.md
├── lessons/index.md
├── references/
│   ├── index.md
│   ├── resources.md
│   └── glossary.md
├── index.md
└── mission.md
learning-records/
NOTES.md
```

1. **`docs/index.md`**: Master portal home with quick navigation cards and Mermaid roadmap.
2. **`docs/mission.md`**: Mission compass (Why, Success looks like, Constraints, Out of scope).
3. **`docs/lessons/index.md`**: 6–9 progressive curriculum modules with 30–60 sequential lesson trackers.
4. **`docs/cheatsheet/index.md`**: Fast syntax, annotation, and command reference catalog.
5. **`docs/debugging/index.md`**: Diagnostic guide catalog for common runtime failures.
6. **`docs/interview/index.md`**: Senior technical and system design question bank.
7. **`docs/references/`**: Hub index (`index.md`), curated resources (`resources.md`), and living glossary (`glossary.md`).
8. **`learning-records/`**: Directory for ADR-style decision records.
9. **`NOTES.md`**: Learner profile, pedagogical preferences, and active module state.

> **Completion Criterion**: All 10 documentation files exist, contain `<topic>`-tailored content with valid Mermaid diagrams, and resolve all relative markdown links without broken references.

---

### Step 5: Install `/teach` Skill & Companion Files

Scaffold the `/teach` skill and verification tooling into `.agents/skills/teach/` from [TEACH-SKILL-TEMPLATE.md](TEACH-SKILL-TEMPLATE.md):

1. Create target directories:
   ```bash
   mkdir -p .agents/skills/teach/agents .agents/skills/teach/scripts
   ```
2. Write the 7 skill components from [TEACH-SKILL-TEMPLATE.md](TEACH-SKILL-TEMPLATE.md):
   - `.agents/skills/teach/SKILL.md`
   - `.agents/skills/teach/MISSION-FORMAT.md`
   - `.agents/skills/teach/LEARNING-RECORD-FORMAT.md`
   - `.agents/skills/teach/RESOURCES-FORMAT.md`
   - `.agents/skills/teach/GLOSSARY-FORMAT.md`
   - `.agents/skills/teach/agents/openai.yaml`
   - `.agents/skills/teach/scripts/validate_mermaid.py`
3. Make the validation script executable:
   ```bash
   chmod +x .agents/skills/teach/scripts/validate_mermaid.py
   ```

> **Completion Criterion**: `.agents/skills/teach/SKILL.md`, `scripts/validate_mermaid.py` (executable), and all 5 specification files exist in `.agents/skills/teach/`.

---

### Step 6: Validate & Build Site

1. Run Zensical build to verify configuration and asset links:
   ```bash
   uv run zensical build --clean
   ```
2. Verify exit status is 0 and `site/index.html` is generated without warnings or broken links.
3. Present summary to the user and prompt them to begin learning with `/teach`.

> **Completion Criterion**: `uv run zensical build --clean` exits with returncode 0 and produces `site/`.

---

## Disclosed Reference

- [SVGL-INTEGRATION.md](SVGL-INTEGRATION.md): SVGL logo URLs, download commands, and fallback SVG generator.
- [ZENSICAL-CONFIG-TEMPLATE.md](ZENSICAL-CONFIG-TEMPLATE.md): Canonical `zensical.toml` and `.github/workflows/docs.yml` templates.
- [CURRICULUM-TEMPLATES.md](CURRICULUM-TEMPLATES.md): Portal templates for `docs/`, `learning-records/`, and `NOTES.md`.
- [TEACH-SKILL-TEMPLATE.md](TEACH-SKILL-TEMPLATE.md): Full `/teach` skill specifications and validation scripts.
