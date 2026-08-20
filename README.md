# GCP Data Engineer Masterclass

Interactive [Zensical](https://zensical.org) teaching workspace and curriculum portal for Google Cloud Platform (GCP) Data Engineering.

## 🚀 Live Portal

Published on GitHub Pages: [https://rohit1024.github.io/data-engineer](https://rohit1024.github.io/data-engineer)

## 📦 Getting Started

### Local Development

1. Ensure [`uv`](https://docs.astral.sh/uv/) is installed.
2. Start the local preview server:
   ```bash
   uv run zensical serve
   ```
3. Build for production:
   ```bash
   uv run zensical build --clean
   ```

## 🛠️ Workspace Structure

- `docs/`: Portal documentation source files.
  - `mission.md`: Learning compass and outcomes.
  - `lessons/`: Structured 8-module progressive curriculum.
  - `cheatsheet/`: Rapid-lookup commands and query syntax.
  - `debugging/`: Troubleshooting playbooks and failure modes.
  - `interview/`: Senior & Lead GCP Data Engineer question bank.
  - `references/`: Living glossary and authoritative resources.
- `.agents/skills/teach/`: `/teach` skill specifications and validation tooling.
- `learning-records/`: ADR-style records tracking demonstrated user mastery.
- `NOTES.md`: Active learner profile and pedagogical preferences.
