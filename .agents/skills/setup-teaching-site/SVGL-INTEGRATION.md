# SVGL Integration & Theme Logo Guide

Zensical allows using custom SVG icons for header logos, browser favicons, and inline markdown emojis via the `overrides/.icons` directory.

---

## 1. SVGL Logo Retrieval

[SVGL](https://svgl.app) provides curated, high-quality SVG logos for developer tools, languages, frameworks, and cloud platforms. Its raw repository is hosted at `pheralb/svgl` on GitHub.

### Direct Download URL Pattern

```text
https://raw.githubusercontent.com/pheralb/svgl/main/static/library/<slug>.svg
```

### Common Slugs Reference

| Topic / Framework | Slug | Download URL |
| :--- | :--- | :--- |
| **Spring / Spring Boot** | `spring` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/spring.svg` |
| **Kubernetes** | `kubernetes` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/kubernetes.svg` |
| **Docker** | `docker` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/docker.svg` |
| **Rust** | `rust` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/rust.svg` |
| **Python** | `python` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/python.svg` |
| **Go** | `go` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/go.svg` |
| **Kafka** | `kafka` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/kafka.svg` |
| **Redis** | `redis` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/redis.svg` |
| **PostgreSQL** | `postgresql` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/postgresql.svg` |
| **GraphQL** | `graphql` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/graphql.svg` |
| **React** | `react` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/react.svg` |
| **TypeScript** | `typescript` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/typescript.svg` |
| **AWS** | `aws` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/aws.svg` |
| **Google Cloud** | `google-cloud` | `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/google-cloud.svg` |

---

## 2. Directory Layout in Zensical

Place the retrieved `.svg` into three destination paths:

```text
overrides/
└── .icons/
    ├── custom/
    │   └── <topic-slug>.svg      <-- Used as site logo: "custom/<topic-slug>"
    └── svgl/
        └── <topic-slug>.svg      <-- Used as markdown emoji: :svgl-<topic-slug>:
docs/
└── assets/
    └── <topic-slug>-logo.svg     <-- Used as browser tab favicon
```

### Retrieval Commands

```bash
SLUG="<topic-slug>" # e.g. kubernetes, rust, spring, etc.
mkdir -p overrides/.icons/custom overrides/.icons/svgl docs/assets

# Fetch from SVGL GitHub raw endpoint
curl -sSL "https://raw.githubusercontent.com/pheralb/svgl/main/static/library/${SLUG}.svg" -o "overrides/.icons/custom/${SLUG}.svg"

# Mirror to svgl folder and assets favicon
cp "overrides/.icons/custom/${SLUG}.svg" "overrides/.icons/svgl/${SLUG}.svg"
cp "overrides/.icons/custom/${SLUG}.svg" "docs/assets/${SLUG}-logo.svg"
```

---

## 3. Zensical Configuration Binding

Bind the SVG in `zensical.toml`:

```toml
[project.theme]
custom_dir = "overrides"
favicon = "assets/<topic-slug>-logo.svg"

[project.theme.icon]
logo = "custom/<topic-slug>"

[project.markdown_extensions.pymdownx.emoji]
emoji_index = "zensical.extensions.emoji.twemoji"
emoji_generator = "zensical.extensions.emoji.to_svg"
options.custom_icons = ["overrides/.icons"]
```

---

## 4. Fallback Clean SVG Generator

If an offline environment or unlisted slug is encountered, write a clean, vectorized SVG icon:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <rect width="64" height="64" rx="12" fill="#3B82F6"/>
  <text x="32" y="40" font-family="system-ui, -apple-system, sans-serif" font-size="28" font-weight="bold" text-anchor="middle" fill="#FFFFFF">T</text>
</svg>
```
*(Replace background fill `#3B82F6` and letter `T` to reflect the topic)*
