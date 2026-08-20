# Learning Record Format

Learning records live in `./learning-records/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`, etc. Create the directory lazily — only when the first record is written.

They are the teaching equivalent of ADRs: they capture non-obvious lessons, key insights, and stated prior knowledge that will steer future sessions. They are used to calculate the zone of proximal development.

## Template

```md
# {Short title of what was learned or established}

{1-3 sentences: what was learned (or what prior knowledge was established), and why it matters for future sessions.}
```

## Optional sections

- **Status** frontmatter (`active | superseded by LR-NNNN`)
- **Evidence** — how the user demonstrated the understanding.
- **Implications** — what this unlocks or rules out for future sessions.

## Numbering

Scan `./learning-records/` for the highest existing number and increment by one.

## When to write a learning record

1. **The user demonstrated genuine understanding of something non-trivial**.
2. **The user disclosed prior knowledge** — "I already know X."
3. **A misconception was corrected**.
4. **The mission shifted in response to learning**.
