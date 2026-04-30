# dbt Architect Exam Study Materials

Community study materials for the **dbt Architect certification exam**. Built from the official dbt documentation and organized around the 8 exam topic areas.

> [!important]
> **Read this first.** This material is my best effort at synthesizing the publicly available [dbt documentation](https://docs.getdbt.com) with LLM assistance, captured as a snapshot in **April 2026**. Treat it as a study aid, not gospel — mistakes are possible, and dbt evolves quickly, so verify anything critical against the current docs. This repo is **not actively maintained** — fork it, adapt it, use it however helps you. If content has drifted, an LLM can help reconcile sections against the latest docs.

## Get the files

```bash
# Clone (recommended — get updates with `git pull`)
git clone https://github.com/<owner>/<repo>.git

# Or download a one-time zip from the GitHub UI:
# green "Code" button → "Download ZIP"
```

> Best viewed in **Obsidian** — answers are collapsible callouts that stay hidden until you click. See [VIEWING.md](VIEWING.md) for setup in Obsidian, GitHub, VS Code, Typora, Notion, and a `<details>`-tag fallback for plain markdown.

## Contents

| File | Description |
|---|---|
| [`study_notes.md`](study_notes.md) | Comprehensive notes covering all 8 topics — UI fields, gotchas, Q&A |
| [`cheat_sheet.md`](cheat_sheet.md) | Condensed pre-exam reference with tables and must-know gotchas |
| [`high_yield_one_pager.md`](high_yield_one_pager.md) | High-yield topics distilled into a single pre-exam page |
| [`exam_topics.md`](exam_topics.md) | Official exam topic outline |

---

## Practice Exam — 234 Questions

> [!note]
> **Scope and intent.** Topics 1–8 mirror the official exam outline (see [`exam_topics.md`](exam_topics.md)). Topics 9–11 (Hooks & Operations, dbt Commands, Model Governance) were added based on focused topics I saw on the actual exam and thought it helpful to add specific notes. These practice questions are **not meant to replicate exam questions** — they're written to help you study each topic in the format and depth the real exam uses.

> ⭐ = High-Yield question. Aim to nail every ⭐ before exam day.
> In Obsidian, switch to **reading mode** (`Cmd+E`) and click each `Answer & Explanations` callout to reveal the answer and per-option explanations. In other tools, see [VIEWING.md](VIEWING.md).

| # | Topic | File | Questions |
|---|---|---|---|
| 1 | Warehouse Connections | [q01_warehouse_connections.md](practice_exam/q01_warehouse_connections.md) | 20 |
| 2 | Git Connections | [q02_git_connections.md](practice_exam/q02_git_connections.md) | 20 |
| 3 | Environments & Schema Generation | [q03_environments.md](practice_exam/q03_environments.md) | 20 |
| 4 | Jobs & CI/CD | [q04_jobs_cicd.md](practice_exam/q04_jobs_cicd.md) | 20 |
| 4c | Blue/Green Deployments | [q05_blue_green.md](practice_exam/q05_blue_green.md) | 20 |
| 5 | Security & Licenses | [q06_security_licenses.md](practice_exam/q06_security_licenses.md) | 22 |
| 6 | Monitoring & Alerting | [q07_monitoring_alerting.md](practice_exam/q07_monitoring_alerting.md) | 20 |
| 7 | dbt Mesh & Cross-Project Refs | [q08_dbt_mesh.md](practice_exam/q08_dbt_mesh.md) | 23 |
| 8 | dbt Catalog | [q09_catalog.md](practice_exam/q09_catalog.md) | 23 |
| 9 | Hooks & Operations | [q10_hooks_operations.md](practice_exam/q10_hooks_operations.md) | 20 |
| 10 | dbt Commands | [q11_dbt_commands.md](practice_exam/q11_dbt_commands.md) | 21 |
| 11 | Model Governance | [q12_model_governance.md](practice_exam/q12_model_governance.md) | 5 |
| | **Total** | | **234** |

### High-Yield Topics Covered (⭐)
- Cross-project environment resolution table (Mesh)
- Deferral: when it breaks, self-deferral first-run behavior
- License types overriding group permissions (IT, Read-Only traps)
- CI job: temp schema lifecycle, smart cancellation, no run slots
- Command ordering: `dbt build` before `dbt sl validate`; checkbox vs step
- Service token: one-time visibility, IP 403, rotation pattern
- Webhook: 5-failure silent auto-disable; `errored` vs `completed` timing
- `--state` + `--target-path` manifest overwrite
- Advanced CI: `event_time` false positives, PII cache masking
- Enterprise+ feature gate (cross-project refs, column lineage, Advanced CI)

---

## Exam Topics

| # | Topic |
|---|---|
| 1 | Configuring dbt data warehouse connections |
| 2 | Configuring dbt git connections |
| 3 | Creating and maintaining dbt environments |
| 4 | Creating and maintaining job definitions |
| 5 | Configuring dbt security and licenses |
| 6 | Setting up monitoring and alerting for jobs |
| 7 | Setting up a dbt Mesh and leveraging cross-project references |
| 8 | Configuring and using dbt Catalog |

## Audio Files

Audio versions of each topic (MP3) are not committed to this repo due to file size. Generate your own with [Microsoft Edge TTS](https://github.com/rany2/edge-tts):

```bash
pip install edge-tts
edge-tts --voice en-GB-RyanNeural --text "$(cat study_notes.md)" --write-media topic_output.mp3
```

For per-topic generation, extract each topic section into a separate text file before running edge-tts. Recommended listening: import to **Overcast** on iPhone and play at 1.3×–1.5× speed.

## Format reference (for forkers)

If you fork and add your own practice questions, the existing `q*.md` files follow this template so callouts collapse correctly in Obsidian:

````markdown
### Q<n>. <optional ⭐ for high-yield>
> **Subdomain X.Y — short topic label**

<question prose>

- A) <option>
- B) <option>
- C) <option>
- D) <option>

> [!success]- Answer & Explanations
> **✅ Correct: <letter>**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | <why> |
> | **B) ✅ Correct** | <why> |
> | **C) ❌ Incorrect** | <why> |
> | **D) ❌ Incorrect** | <why> |
>
> > 💡 **Key rule**: <one-liner takeaway>

---
````

Keep the `> [!success]-` form (with trailing `-`) so Obsidian renders the callout collapsed by default. See [VIEWING.md](VIEWING.md) for how this renders in non-Obsidian tools.

## Source

Study notes derived from the official [dbt documentation](https://docs.getdbt.com) and dbt Cloud UI behavior.

## License

Released under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) license. Use, share, adapt, or build on this material — including commercially — as long as you give credit. See [`LICENSE`](LICENSE) for the full terms.
