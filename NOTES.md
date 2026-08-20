# User Learning Notes & Preferences

## Learner Profile
- **Starting Point**: Foundational engineering knowledge established; zero to moderate prior Google Cloud Platform (GCP) Data Engineering experience.
- **Primary Goal**: Master production-grade GCP Data Engineering, distributed architectures, streaming, and lakehouses for Senior/Principal Engineering roles.
- **Teaching Strategy**: Bottom-up explanations of internal mechanics (Dremel, Beam runtime, Spark DAG, Colossus), progressing to enterprise distributed patterns.

## Pedagogical Notes & Preferences
- **Mermaid Diagrams**: Always include rich Mermaid diagrams (flowcharts, sequence diagrams, state machines, architecture maps) in every Lesson and Debugging guide to clearly visualize runtime behavior.
- **Zensical Navigation**: Keep `zensical.toml` sidebar clean (top-level section tabs only); maintain detailed catalogs inside each folder's `index.md`.
- **Bottom Pagination**: Every lesson, cheatsheet, and debugging guide must include a bottom navigation table linking to Previous, Catalog Index, and Next (updating adjacent files as new lessons are published).
- Keep lessons compact and high-yield with runnable code blocks (`gcloud`, Python, SQL, Beam), architectural diagrams, and actionable quizzes/challenges.
- Track mastery with ADR-style learning records in `learning-records/`.
