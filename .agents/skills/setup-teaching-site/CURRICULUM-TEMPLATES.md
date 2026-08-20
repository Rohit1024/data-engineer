# Portal Hierarchy & Curriculum Templates

This document details the standard file templates for scaffolding the `docs/` tree, `learning-records/`, and `NOTES.md`.

---

## 1. `docs/index.md` (Home Portal)

```markdown
---
icon: lucide/rocket
---

# {TOPIC_TITLE} Masterclass

Welcome to your dedicated learning workspace for **{TOPIC_TITLE}**.

This portal is structured to take you from core fundamentals to designing, debugging, and deploying production-grade systems.

---

## 🎯 Quick Navigation

- 🧭 [**The Mission**](mission.md) — The guiding compass and outcomes for this workspace.
- 🎓 [**Curriculum & Lessons**](lessons/index.md) — Progressive modules covering in-depth lessons.
- ⚡ [**Cheatsheets**](cheatsheet/index.md) — Fast lookups, annotation tables, and command references.
- 🔍 [**Debugging Guides**](debugging/index.md) — Practical diagnostic workflows and failure mode resolution.
- 💼 [**Interview Questions**](interview/index.md) — High-signal technical and system design interview questions.
- 📚 [**References & Glossary**](references/index.md) — Canonical terminology and authoritative documentation sources.

---

## 🏛️ Masterclass Modules Roadmap

``` mermaid
flowchart TB
    M1["1. Core Fundamentals"] --> M2["2. Core APIs & Architecture"]
    M2 --> M3["3. Persistence & State Management"]
    M3 --> M4["4. Tooling, Observability & Docs"]
    M4 --> M5["5. Security, Auth & Permissions"]
    M5 --> M6["6. Enterprise Testing & QA"]
    M6 --> M7["7. Caching, Events & Messaging"]
    M7 --> M8["8. Distributed Patterns & Cloud Deployment"]
    M8 --> M9["9. Advanced Ecosystem & AI Integration"]
```

---

## 🚀 Get Started Immediately

Dive straight into **Module 1**:
👉 [**Curriculum & First Lesson**](lessons/index.md)
```

---

## 2. `docs/mission.md` (Guiding Compass)

```markdown
---
icon: lucide/compass
---

# Mission: {TOPIC_TITLE} Mastery

## Why

Transition from foundational knowledge to architecting, debugging, and shipping production-grade systems using **{TOPIC_TITLE}**. Build deep mental models, high-signal enterprise portfolio projects, and master architectural trade-offs required for senior engineering roles.

## Success looks like

- Writing clean, idiomatic, production-grade {TOPIC_TITLE} code from scratch with zero boilerplate confusion.
- Mastering internal runtime mechanics, lifecycles, and core architectural abstractions.
- Implementing zero-trust security, authentication, and access control.
- Designing resilient distributed architectures, event-driven pipelines, and caching patterns.
- Containerizing and orchestrating services with automated CI/CD deployment.
- Writing comprehensive test suites (unit, integration, and mock suites).
- Troubleshooting complex runtime failures, race conditions, and bottlenecks using diagnostic playbooks.

## Constraints

- Built bottom-up from first principles (explaining *how* the system works under the hood).
- Every concept backed by runnable code, architectural Mermaid diagrams, and real-world system trade-offs.

## Out of scope

- Outdated legacy patterns superseded in modern versions.
```

---

## 3. `docs/lessons/index.md` (Curriculum Catalog)

Organize the curriculum into 6–9 structured modules (30–60 lessons total) with checkbox trackers:

```markdown
---
icon: lucide/graduation-cap
---

# {TOPIC_TITLE} Curriculum

All concepts from your comprehensive roadmap are organized into structured, progressive modules. Each lesson is focused, hands-on, and includes architectural diagrams, internal mechanics, and retrieval exercises.

---

## 🏛️ Module 1: Core Fundamentals & Runtime Internals
- [ ] **0001: Architecture Overview, Core Primitives & Lifecycle**
- [ ] **0002: Dependency Management & Configuration Mechanics**
- [ ] **0003: Core Engine Under the Hood: Startup & Pipeline Internals**
- [ ] **0004: Execution Context, Interceptors & Middleware**
- [ ] **0005: Environment Management & Profiles (`dev`, `stage`, `prod`)**

---

## 🌐 Module 2: Core APIs, Protocols & Data Flow
- [ ] **0006: Protocol Architecture & Request/Response Pipelines**
- [ ] **0007: Building RESTful / RPC APIs & Status Codes**
- [ ] **0008: Schema Validation & Constraint Enforcements**
- [ ] **0009: Global Error Handling & Standardized Response Envelopes**
- [ ] **0010: Idiomatic Data Transfer & Mapping Patterns**

---

## 💾 Module 3: Persistence, Storage & State Management
- [ ] **0011: Storage Engine Internals & Data Access Layers**
- [ ] **0012: Query Construction, Indexing & Execution Optimization**
- [ ] **0013: Transaction Boundaries, Isolation Levels & Consistency**
- [ ] **0014: Relational vs Document Storage Integration**

---

## 🛠️ Module 4: Observability, Metrics & Diagnostics
- [ ] **0015: Structured Logging & Distributed Trace Context**
- [ ] **0016: Production Health Probes, Metrics & Alerting**
- [ ] **0017: Interactive API Documentation & OpenAPI/Swagger**

---

## 🔒 Module 5: Security, Identity & Access Control
- [ ] **0018: Authentication Architecture & Token Lifecycles (JWT, OAuth2)**
- [ ] **0019: Role-Based & Attribute-Based Access Control (RBAC/ABAC)**
- [ ] **0020: Secure Secret Management & TLS Termination**

---

## 🧪 Module 6: Testing & Quality Assurance
- [ ] **0021: Unit Testing Frameworks & Assertion Libraries**
- [ ] **0022: Mocking Boundaries & Dependency Isolation**
- [ ] **0023: End-to-End Integration Testing with Ephemeral Containers**

---

## ⚡ Module 7: High-Performance Caching & Event Messaging
- [ ] **0024: In-Memory Caching Strategies (Redis, Memcached) & Invalidation**
- [ ] **0025: Event Fanout, Message Queues & Consumer Groups**
- [ ] **0026: Distributed Rate Limiting & Backpressure Strategies**

---

## 🧩 Module 8: Distributed Systems, Containers & Cloud Deployment
- [ ] **0027: Service Decomposition & Boundary Design**
- [ ] **0028: Multi-Stage Docker Builds & Minimal Images**
- [ ] **0029: Kubernetes Pods, Deployments & Service Networking**
- [ ] **0030: Cloud CI/CD Automation & Zero-Downtime Rollouts**
```

---

## 4. `docs/cheatsheet/index.md` (Cheatsheet Catalog)

```markdown
---
icon: lucide/file-code
---

# Architecture & Command Cheatsheets

Quick-reference guides, operational checklists, and condensed code snippets for each module.

- [ ] **Core Architecture & Syntax Cheatsheet** *(Module 1)*
- [ ] **APIs & Data Transformation Cheatsheet** *(Module 2)*
- [ ] **Persistence & Query Patterns Cheatsheet** *(Module 3)*
- [ ] **Security & Token Configuration Cheatsheet** *(Module 5)*
- [ ] **Docker & Kubernetes Deployment Cheatsheet** *(Module 8)*
- [ ] **Messaging & Caching Cheatsheet** *(Module 7)*
```

---

## 5. `docs/debugging/index.md` (Debugging Catalog)

```markdown
---
icon: lucide/bug
---

# {TOPIC_TITLE} Debugging & Diagnostic Guides

Practical troubleshooting workflows, root-cause analyses, and diagnostic playbooks for common {TOPIC_TITLE} failures.

---

## 🔍 Diagnostic Guides

- [ ] **Startup & Dependency Initialization Failures** *(Module 1)*
- [ ] **API Validation, Serialization & Deserialization Errors** *(Module 2)*
- [ ] **Database Connection Pool Exhaustion & Query Latency Spikes** *(Module 3)*
- [ ] **Authentication Token Verification & CORS Rejections** *(Module 5)*
- [ ] **Distributed Consumer Lag & Message Loss Troubleshooting** *(Module 7)*
- [ ] **Container OOMKilled & Deadlock Diagnostic Workflows** *(Module 8)*
```

---

## 6. `docs/interview/index.md` (Interview Q&A Catalog)

```markdown
---
icon: lucide/help-circle
---

# Senior {TOPIC_TITLE} & System Design Interview Questions

Curated, high-signal technical and architectural interview questions for Senior Engineering roles.

---

## 🏛️ Core Architecture & Runtime Mechanics
- **Runtime Lifecycle**: Explain the step-by-step startup sequence and internal execution model.
- **Concurrency & State**: How does {TOPIC_TITLE} manage thread safety, connection pools, and memory allocation under load?

---

## 🌐 API Design & Communication
- **Pipeline Architecture**: Walk through request handling from ingress network socket to controller handler.
- **Idempotency & Resilience**: How do you guarantee idempotency and graceful degradation during downstream outages?

---

## 💾 Persistence, Transactions & Caching
- **Transaction Isolation**: Compare transaction propagation and isolation semantics.
- **Cache Stampede Prevention**: How do you prevent cache breakdown under extreme concurrency?

---

## ⚡ Distributed Systems & Cloud
- **Zero-Loss Messaging**: How do you guarantee at-least-once or exactly-once message delivery?
- **High-Availability & Partition Tolerance**: Discuss CAP theorem trade-offs for {TOPIC_TITLE} deployments.
```

---

## 7. `docs/references/` Files

### `docs/references/index.md`
```markdown
---
icon: lucide/book-open
---

# {TOPIC_TITLE} References & Standards

Welcome to the reference library. Here you will find authoritative documentation, deep-dive architectural references, and the living glossary for our masterclass.

- [**Curated Resources & Communities**](resources.md): High-trust documentation, source books, and developer communities.
- [**Living Glossary**](glossary.md): Clear definitions for core terms and architectural patterns used across all lessons.
```

### `docs/references/resources.md`
```markdown
# {TOPIC_TITLE} Resources

## Knowledge

- [Official Documentation](https://example.com)
  Authoritative specification, reference manuals, and API guides. Use for: core syntax and configuration.
- [Architecture & Design Source Book](https://example.com)
  Foundational text on internal mechanics and best practices.

## Wisdom (Communities)

- [Topic Subreddit / Forum](https://example.com)
  High-signal developer community for real-world architecture critiques and debugging.
- [Official Discord / Slack](https://example.com)
  Real-time practitioner chat and ecosystem updates.
```

### `docs/references/glossary.md`
```markdown
# {TOPIC_TITLE} Glossary

Canonical nomenclature and standard terminology used across all lessons in this workspace.

## Terms

**Runtime Engine**:
The underlying process executing instructions, managing lifecycles, and scheduling tasks.

**Inversion of Control (IoC)**:
Architectural pattern where framework code controls execution flow rather than application code.
```

---

## 8. `NOTES.md` (Teaching Scratchpad)

```markdown
# User Learning Notes & Preferences

## Learner Profile
- **Starting Point**: Foundational engineering knowledge established; zero to moderate prior {TOPIC_TITLE} experience.
- **Primary Goal**: Master production-grade {TOPIC_TITLE} and distributed architectures for Senior Engineering roles.
- **Teaching Strategy**: Bottom-up explanations of internal mechanics, progressing to enterprise distributed patterns.

## Pedagogical Notes & Preferences
- **Mermaid Diagrams**: Always include rich Mermaid diagrams (flowcharts, sequence diagrams, state machines, architecture maps) in every Lesson and Debugging guide to clearly visualize runtime behavior.
- **Zensical Navigation**: Keep `zensical.toml` sidebar clean (top-level section tabs only); maintain detailed catalogs inside each folder's `index.md`.
- **Bottom Pagination**: Every lesson, cheatsheet, and debugging guide must include a bottom navigation table linking to Previous, Catalog Index, and Next (updating adjacent files as new lessons are published).
- Keep lessons compact and high-yield with runnable code blocks, architectural diagrams, and actionable quizzes/challenges.
- Track mastery with ADR-style learning records in `learning-records/`.
```
