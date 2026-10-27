# User Learning Notes & Preferences

## Learner Profile
- **Starting Point**: Foundational engineering knowledge established; zero to moderate prior Google Cloud Platform (GCP) Data Engineering experience.
- **Primary Goal**: Master production-grade GCP Data Engineering, distributed architectures, streaming, and lakehouses for Senior/Principal Engineering roles.
- **Teaching Strategy**: Bottom-up explanations of internal mechanics (Dremel, Beam runtime, Spark DAG, Colossus), progressing to enterprise distributed patterns.

## Pedagogical Notes & Preferences
- **Mermaid Diagrams**: Always include rich Mermaid diagrams (flowcharts, sequence diagrams, state machines, architecture maps) in every Lesson and Debugging guide to clearly visualize runtime behavior.
- **Zensical Navigation**: Keep `zensical.toml` sidebar clean (top-level section tabs only); maintain detailed catalogs inside each folder's `index.md`.
- **Bottom Pagination**: Every lesson, cheatsheet, and debugging guide must include a bottom navigation table linking to Previous, Catalog Index, and Next (updating adjacent files as new lessons are published).
- Explain important topics with concrete mechanics, worked examples, expected outcomes and actionable recall/failure exercises. Keep summaries concise without replacing the detailed explanation.
- Track mastery with ADR-style learning records in `learning-records/`.

## Curriculum review

- On 2026-10-28, reviewed all 40 original lessons and added lessons 0041–0045 for modeling, contracts, platform identity/networking, recovery objectives and architecture sizing. See `docs/references/curriculum-audit.md` for findings and validation scope. Authored lessons do not establish demonstrated learner mastery.
