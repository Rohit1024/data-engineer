---
name: teach
description: Teach a concept step-by-step within this workspace.
disable-model-invocation: true
argument-hint: "What would you like to learn about?"
---

# Teaching Workspace

Guide the user through multi-session learning grounded in the workspace state.

## Workspace State

- `docs/mission.md`: The guiding compass and user goals. Ground all teaching here. See [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `docs/lessons/`: Sequential lessons (`NNNN-<slug>.md`). Maintained in `docs/lessons/index.md`.
- `docs/cheatsheet/`: Compressed commands, annotations, and quick references.
- `docs/debugging/`: Diagnostic playbooks with failure sequence diagrams.
- `docs/interview/`: Senior technical and system design question bank.
- `docs/references/`: Official sources (`resources.md`), glossary (`glossary.md`), and reference index (`index.md`).
- `learning-records/`: ADR-style records of demonstrated user understanding (`NNNN-<slug>.md`). See [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `NOTES.md`: Scratchpad for learner profile and working notes.

## Core Rules

1. **Ground in Mission**: Align every lesson with `docs/mission.md`. If unclear, interview the user first.
2. **High-Trust Knowledge**: Source facts from `docs/references/resources.md`. Verify facts before explaining.
3. **Storage Strength**: Build retention through active recall, desirable difficulty, and hands-on exercises.

## Authoring Lessons

1. **File Location**: Save self-contained lessons to `docs/lessons/NNNN-<slug>.md`.
2. **Catalog Updates**: Check off and link every new lesson in `docs/lessons/index.md`.
3. **Sidebar Rule**: Expose only top-level section roots in `zensical.toml` `nav` (e.g. `{ "Lessons" = ["lessons/index.md"] }`). Keep individual lessons cataloged inside `docs/lessons/index.md`.
4. **Bottom Pagination**: Include navigation linking `Previous Lesson | All Lessons (index.md) | Next Lesson`. Update the previous lesson's "Next" link when adding a lesson.
5. **Visual Diagrams**: Include vertical Mermaid diagrams in every lesson and debugging guide.
6. **Zensical Styling**: Use admonitions (`!!! note`, `!!! tip`), code annotations, and copy buttons.

## Authoring Reference & Debugging Guides

- Cheatsheets: `docs/cheatsheet/`
- Debugging Playbooks: `docs/debugging/` (include failure sequence diagrams)
- Interview Questions: `docs/interview/`
- Catalog all guides in their section `index.md` with bottom pagination tables.

## Mermaid Standards & Verification

### Layout Standards
- **Orientation**: Default to `flowchart TD` (top-to-bottom).
- **Subgraphs**: Stack parallel architectures vertically (`SubA ~~~ SubB`) to maintain readable node widths.
- **Quoted Labels**: Quote node labels with special characters (e.g., `Node["Item (Details)"]`).

### Verification Steps
Run automated verification before completing your turn:

1. Validate Mermaid syntax (must report 0 errors):
   ```bash
   python3 .agents/skills/teach/scripts/validate_mermaid.py
   ```
2. Validate documentation build:
   ```bash
   uv run zensical build
   ```
3. Report completion summary:
   - Number of Mermaid diagrams validated (0 syntax errors).
   - Zensical build status.
