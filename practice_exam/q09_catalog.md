# Topic 8: dbt Catalog — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 23 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 8.1 — CI jobs do not update Catalog**

A team runs CI jobs on every pull request and a scheduled deployment job every 24 hours. They notice that the dbt Catalog is not reflecting model changes that landed in CI runs during the day — only overnight changes appear. What is the cause?

- A) CI jobs have a 12-hour delay before Catalog updates reflect their changes.
- B) CI jobs **do not update Catalog metadata** — only deployment jobs (scheduled or manual) in production or staging environments do.
- C) The Catalog only updates when `dbt docs generate` is run as a standalone command, not as a checkbox.
- D) CI jobs update Catalog but only for models that passed all tests.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no delayed Catalog update for CI jobs — they are explicitly excluded from Catalog updates. |
> | **B) ✅ Correct** | CI jobs are explicitly excluded from updating dbt Catalog metadata. Only **deployment jobs** (scheduled or manually triggered) running in production or staging environments update the Catalog. This is by design — CI builds temp schemas that don't represent production state. The team's overnight deployment job is the correct Catalog updater. |
> | **C) ❌ Incorrect** | The `dbt docs generate` checkbox in a deployment job does update Catalog — the key is that it must be in a deployment job, not a CI job. |
> | **D) ❌ Incorrect** | CI test pass/fail status has no bearing on whether CI jobs update Catalog — they simply don't update it at all. |
>
> > 💡 **Key rule**: CI jobs = **never update Catalog**. Only production/staging deployment jobs with `dbt docs generate` update Catalog.

---

### Q2. ⭐
> **Subdomain 8.2 — Catalog inactivity purge**

A team has a `sandbox` environment in dbt Cloud that runs experimental jobs. The environment hasn't had a successful job run in 4 months. What happens to this environment in dbt Catalog?

- A) The environment remains in Catalog indefinitely — only manual deletion removes it.
- B) The environment is automatically purged from Catalog after 3 months of no successful job runs.
- C) The environment is flagged as "Inactive" in Catalog but remains visible.
- D) The environment is purged after 6 months of inactivity.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Environments are not retained indefinitely — there is an auto-purge policy. |
> | **B) ✅ Correct** | Environments with **no successful job run in 3+ months** are automatically removed from dbt Catalog. The 4-month inactive `sandbox` environment would already be purged. To keep an environment visible in Catalog, schedule at least one lightweight job (even `dbt compile`) to run successfully at least quarterly. |
> | **C) ❌ Incorrect** | There is no "Inactive" flagging status — inactive environments are fully purged. |
> | **D) ❌ Incorrect** | The threshold is **3 months**, not 6 months. |
>
> > 💡 **Key rule**: No successful run in **3+ months** = environment auto-purged from Catalog. Run at least quarterly to stay visible.

---

### Q3.
> **Subdomain 8.3 — Column-level lineage limitations**

An Enterprise+ team is excited about column-level lineage in dbt Catalog. They have a mix of SQL and Python models in their project. For which models will column-level lineage be available?

- A) All models — column-level lineage works for both SQL and Python models on Enterprise+.
- B) SQL models only — column-level lineage does not work for Python models (their internals are opaque to dbt's parser).
- C) Only models using the `table` or `incremental` materialization — views are excluded.
- D) Only models with `contract: enforced: true` — contracts are required for column-level lineage.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Column-level lineage explicitly does NOT work for Python models regardless of plan. |
> | **B) ✅ Correct** | Column-level lineage in dbt Catalog is available for **SQL models only** (Enterprise+). Python model internals are opaque to dbt's SQL lineage parser — it cannot trace column transformations through Python code. If a team has high-value Python models, column-level lineage will not be available for those specific models. |
> | **C) ❌ Incorrect** | Column-level lineage works for all SQL materialization types, not just table/incremental. |
> | **D) ❌ Incorrect** | Contracts are not a prerequisite for column-level lineage — they are separate concepts. |
>
> > 💡 **Key rule**: Column-level lineage = Enterprise+ AND **SQL models only**. Python models = opaque to parser.

---

### Q4.
> **Subdomain 8.4 — What catalog.json contains vs manifest.json**

A data engineer is debugging why the dbt Catalog shows incorrect column types for a model. They need to understand which artifact file to inspect. What does `catalog.json` contain that `manifest.json` does not?

- A) `catalog.json` contains the compiled SQL for each model; `manifest.json` contains the raw Jinja.
- B) `catalog.json` contains column-level information (names, types, row counts) introspected directly from the database; `manifest.json` contains model metadata and lineage from the dbt project.
- C) `catalog.json` contains run results and test outcomes; `manifest.json` contains model definitions.
- D) `catalog.json` contains environment variable values; `manifest.json` contains connection details.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Compiled SQL is in the `target/` directory as individual `.sql` files, or in `manifest.json`'s compiled SQL field — not `catalog.json`. |
> | **B) ✅ Correct** | `catalog.json` is produced by `dbt docs generate` and contains **database-introspected column information** — actual column names, data types, and row counts as they exist in the warehouse. `manifest.json` contains dbt project metadata: model definitions, lineage graph, configs, node relationships. |
> | **C) ❌ Incorrect** | Run results and test outcomes are in `run_results.json` — not `catalog.json`. |
> | **D) ❌ Incorrect** | Environment variables and connection details are not stored in either `catalog.json` or `manifest.json`. |
>
> > 💡 **Key rule**: `catalog.json` = **warehouse-introspected column info** (names, types, row counts). `manifest.json` = project metadata and lineage.

---

### Q5.
> **Subdomain 8.5 — Multiple jobs generating artifacts**

A team has two deployment jobs both configured to generate documentation for the same dbt project. What is the risk?

- A) No risk — dbt Cloud merges artifact outputs from multiple jobs to produce a comprehensive Catalog.
- B) The jobs will overwrite each other's artifacts — the Catalog will reflect whichever job ran last, potentially showing an inconsistent or incomplete state.
- C) dbt Cloud automatically deduplicates artifact outputs when multiple jobs generate docs.
- D) The second job fails automatically when it detects another job is already generating artifacts for the same project.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt Cloud does not merge artifacts — each job write overwrites the previous one. |
> | **B) ✅ Correct** | When multiple jobs are both designated for artifact generation, they **overwrite each other's artifacts** — the Catalog reflects whatever job ran last. If the jobs run at different times covering different scopes, the Catalog state can be inconsistent or incomplete. Best practice: designate **exactly one job per project** for artifact generation. |
> | **C) ❌ Incorrect** | There is no deduplication logic for artifacts. |
> | **D) ❌ Incorrect** | There is no lock or failure mechanism preventing concurrent artifact generation — they simply overwrite each other. |
>
> > 💡 **Key rule**: **One job per project** for artifact generation. Multiple jobs = conflicting/overwritten artifacts = inconsistent Catalog.

---

### Q6. ⭐
> **Subdomain 8.6 — Model Query History**

A team wants to use dbt Catalog's Model Query History feature to identify which models are most frequently queried by downstream users, in order to prioritize optimization work. What is required to enable this feature?

- A) The feature is available on all dbt Cloud plans — no specific plan required.
- B) Enterprise or Enterprise+ plan, and it must be enabled in the Production environment settings by testing and enabling query history permissions.
- C) Enterprise+ plan only, and it requires the Fusion engine to be enabled.
- D) Starter plan with the Advanced CI feature enabled.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Model Query History is not available on Starter or Developer plans. |
> | **B) ✅ Correct** | Model Query History requires **Enterprise or Enterprise+** plan. To enable it: Orchestration → Environments → select the Production environment → Settings → scroll to Query History → click **"Test Permissions"** → check **"Enable query history"** → Save. It tracks SELECT queries by downstream users/tools (excludes dbt builds and test runs). |
> | **C) ❌ Incorrect** | Fusion engine is required for Cost Insights, not Model Query History. The plan requirement is Enterprise (not Enterprise+). |
> | **D) ❌ Incorrect** | Advanced CI and Model Query History are unrelated features. |
>
> > 💡 **Key rule**: Model Query History = **Enterprise+** plan. Enable in Production env settings. Tracks downstream SELECT queries only (not dbt builds).

---

---

### Q7.
> **Subdomain 8.7 — dbt Docs vs dbt Catalog**

A new team member asks about the difference between `dbt docs generate` (dbt Docs) and dbt Catalog. Which statement is correct?

- A) They are the same product — dbt Catalog is just the new branding for dbt Docs.
- B) dbt Docs generates a static HTML site from project metadata (available on all plans). dbt Catalog is a dynamic real-time metadata platform (available on Starter+ only) with features like lineage, data health, and query history.
- C) dbt Docs is available on Enterprise+; dbt Catalog is available on all plans.
- D) dbt Catalog is built on top of `dbt docs generate` artifacts and requires them to be generated daily.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | They are distinct products with different capabilities, plans, and use cases. |
> | **B) ✅ Correct** | **dbt Docs** (`dbt docs generate`) creates a **static HTML site** from project artifacts — available on **all plans**, self-hosted or served via dbt Cloud. It reflects the state at the time of generation. **dbt Catalog** is a **dynamic, real-time metadata platform** in dbt Cloud that provides lineage, data health signals, query history, and exploration tools — available on **Starter and above**. The Catalog is always up-to-date with production job runs; dbt Docs is a point-in-time snapshot. |
> | **C) ❌ Incorrect** | dbt Docs is available on all plans; dbt Catalog requires Starter+. This is the reverse of the stated answer. |
> | **D) ❌ Incorrect** | dbt Catalog does use artifacts generated by deployment jobs, but it is not simply a wrapper around `dbt docs generate` output. It has its own metadata ingestion and real-time features. |
>
> > 💡 **Key rule**: dbt Docs = static HTML, all plans. dbt Catalog = dynamic real-time metadata, Starter+ only.

---

### Q8.
> **Subdomain 8.8 — Catalog reflects production only**

A developer builds and tests a model in the dbt Cloud IDE in their personal dev schema (`dbt_alice`). They expect to see it appear in dbt Catalog so they can share a lineage link with a stakeholder. The model does not appear in Catalog. Why?

- A) Catalog only indexes models that have been tagged with `+catalog: true` in their config.
- B) dbt Catalog reflects the **production environment only** by default. Dev and staging models do not appear in Catalog until they exist in a production deployment job run.
- C) The model needs to be committed to the main branch before it appears in Catalog.
- D) The developer must manually publish the model to Catalog from the IDE using the "Publish" button.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no `catalog: true` tag requirement. Models appear in Catalog based on which environment they were built in. |
> | **B) ✅ Correct** | dbt Catalog reflects the **production environment only** by default. Models built in developer personal schemas (dev) or staging environments do not surface in Catalog until they have been run through a **production deployment job**. The developer cannot share a Catalog link for an unreleased model — it only appears after the next production run builds it. |
> | **C) ❌ Incorrect** | Committing to main is not sufficient — a production deployment job must actually run and build the model. |
> | **D) ❌ Incorrect** | There is no manual "Publish to Catalog" button in the IDE. |
>
> > 💡 **Key rule**: dbt Catalog = production environment only. Dev/staging models are invisible until built by a production deployment job.

---

### Q9.
> **Subdomain 8.9 — Data health signals**

A stakeholder views a model in dbt Catalog and sees a **"Degraded"** health signal. What does this indicate, and what typically triggers it?

- A) The model has not been run in more than 30 days.
- B) The model's dbt tests are failing or sources feeding it are stale — health signals are driven by test results and source freshness checks.
- C) The model has no description or documentation — degraded means undocumented.
- D) The model has more than 100 downstream consumers, causing performance degradation.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Inactivity does not directly trigger a "Degraded" signal. Inactivity triggers the Catalog purge after 3 months. |
> | **B) ✅ Correct** | Data health signals in dbt Catalog (Healthy / Caution / Degraded) are driven by **test results and source freshness** outcomes from the most recent production job run. **Degraded** indicates that tests are failing or sources are stale — the model's data quality is questionable. **Caution** indicates warnings. **Healthy** means all tests passed and sources are fresh. These signals give data consumers quick visibility into data trustworthiness. |
> | **C) ❌ Incorrect** | Documentation completeness is not a health signal driver. Missing descriptions do not cause a Degraded status. |
> | **D) ❌ Incorrect** | Downstream consumer count is tracked (query history) but is not a health signal. |
>
> > 💡 **Key rule**: Catalog health = Healthy / Caution / Degraded — driven by **test results** and **source freshness**. Degraded = failing tests or stale sources.

---

### Q10.
> **Subdomain 8.10 — Lenses DAG overlays**

A data platform team wants to quickly identify which models in the lineage graph have the most test failures and which are materialized as views vs tables. Which dbt Catalog feature allows this?

- A) The **Filters** panel — allows filtering models by materialization type and test status.
- B) The **Lenses** feature — DAG overlays that color-code nodes by attributes like materialization type, test status, model layer, or consumption query history.
- C) The **Column-level lineage** view — shows test status per column in the lineage graph.
- D) The **Resources** tab — lists all models with sortable columns for materialization and test status.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Filters narrow which nodes are shown; they don't provide a visual DAG overlay. |
> | **B) ✅ Correct** | **Lenses** are visual **DAG overlays** in dbt Catalog's lineage graph. They color-code nodes based on selected attributes. Per the dbt docs, the available lenses are: **Resource type**, **Materialization type**, **Latest status**, **Model layer** (staging / intermediate / marts), **Test status**, and **Consumption query history**. This allows rapid visual identification of problem areas, materialization patterns, or hot/cold consumption directly in the graph. |
> | **C) ❌ Incorrect** | Column-level lineage shows column data flow, not test status overlays on nodes. |
> | **D) ❌ Incorrect** | The Resources tab is a list view — useful for sorting, but does not provide the visual DAG overlay that Lenses provide. |
>
> > 💡 **Key rule**: Lenses = DAG overlays in dbt Catalog. Six lenses available: Resource type, Materialization type, Latest status, Model layer, Test status, Consumption query history. **Cost is NOT a lens** — Cost Insights is a separate Catalog feature.

---

### Q11.
> **Subdomain 8.11 — Cross-project lineage plan requirement**

A data governance lead wants to view lineage that spans multiple dbt projects in dbt Catalog — tracing data flow from raw sources through the Platform project into the Marketing project. What plan is required?

- A) Starter plan — cross-project lineage is included with basic Catalog access.
- B) Enterprise plan — cross-project lineage requires the Enterprise tier.
- C) Enterprise+ plan — cross-project lineage (multi-project DAG view) is an Enterprise+ feature.
- D) No specific plan — cross-project lineage is available on all plans that have dbt Mesh configured.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Starter plan has basic Catalog access but does not include cross-project lineage. |
> | **B) ❌ Incorrect** | Enterprise has many features but multi-project lineage in Catalog is gated to Enterprise+. |
> | **C) ✅ Correct** | **Cross-project lineage** (multi-project DAG view spanning multiple dbt projects) requires **Enterprise+**. This allows the lineage graph to show data flowing across project boundaries — tracing dependencies from upstream foundational projects through downstream consumer projects. It is one of the key Enterprise+ features alongside column-level lineage and project dependencies (dbt Mesh). |
> | **D) ❌ Incorrect** | dbt Mesh configuration (project dependencies) requires Enterprise+, so this is a tautology — but the plan requirement is explicit. |
>
> > 💡 **Key rule**: Cross-project lineage in Catalog = **Enterprise+** required.

---

### Q12.
> **Subdomain 8.12 — Production job designation**

A team has four deployment jobs in their dbt project. They want to designate which job's artifacts are used to populate dbt Catalog. Where in dbt Cloud is this configured, and how many jobs can be designated?

- A) In each job's Advanced Settings → "Publish to Catalog" toggle. All jobs can be toggled on simultaneously.
- B) In Account Settings → select the project → Edit → Artifacts section. **One job per project** should be designated to avoid conflicting artifact states.
- C) In the Production environment settings → "Catalog source job" dropdown. Multiple jobs can be designated.
- D) Automatically — whichever job ran most recently updates Catalog; no manual designation is needed.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no per-job "Publish to Catalog" toggle in job settings. |
> | **B) ✅ Correct** | Artifact designation is configured at: **Account Settings → click account name in left sidebar → select project → Edit → Artifacts section**. Here you select which job generates documentation and source freshness artifacts for Catalog. Only **one job per project** should be designated — if multiple jobs generate artifacts, they overwrite each other's output, causing inconsistent or stale Catalog state. |
> | **C) ❌ Incorrect** | The designation is in Account Settings → project → Artifacts, not in the environment settings. |
> | **D) ❌ Incorrect** | Catalog does not automatically use the most recently run job. The designation is explicit and manual. |
>
> > 💡 **Key rule**: Artifact designation path: Account Settings → project → Edit → Artifacts. One job per project — multiple jobs cause conflicting artifacts.

---

### Q13.
> **Subdomain 8.13 — sources.json contents**

An architect is auditing what each dbt artifact file contains. What information is stored in `sources.json` that is NOT in `manifest.json`?

- A) Source table names and their warehouse locations
- B) **Source freshness check results** — the actual freshness measurements and pass/fail status from the last `dbt source freshness` run
- C) Source-to-model lineage edges
- D) Source schema definitions and column names

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Source table names and locations are defined in the project YAML and appear in `manifest.json` as source node metadata. |
> | **B) ✅ Correct** | `sources.json` contains **source definitions AND freshness check results** — specifically the actual freshness measurements (e.g., time since last update) and the pass/warn/error status from `dbt source freshness` runs. `manifest.json` contains the source definitions but not the runtime freshness results. This is why `sources.json` must be refreshed regularly to reflect current data freshness state in Catalog. |
> | **C) ❌ Incorrect** | Source-to-model lineage is captured in `manifest.json` as part of the project DAG. |
> | **D) ❌ Incorrect** | Source schema definitions (column names, descriptions) are in `manifest.json`. |
>
> > 💡 **Key rule**: `sources.json` = source definitions + **freshness check results** (actual measured freshness + pass/warn/error status). `manifest.json` = project structure, lineage, metadata.

---

### Q14.
> **Subdomain 8.14 — Cost Insights requirements**

A team on dbt Cloud Enterprise wants to use the Cost Insights feature to track Snowflake spend per model. They navigate to the Catalog but cannot find Cost Insights. What requirements are they missing?

- A) Cost Insights is available on Enterprise+ only — they need to upgrade.
- B) Cost Insights requires **Fusion engine enabled** AND **state-aware orchestration enabled** — both must be active. Also note that data refreshes with up to a 24-hour lag.
- C) Cost Insights requires a separate Snowflake cost management integration to be configured by dbt support.
- D) Cost Insights is only available for BigQuery — Snowflake cost tracking uses a different mechanism.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | While Enterprise+ provides additional features, Cost Insights availability depends on Fusion engine and state-aware orchestration, not just plan tier. |
> | **B) ✅ Correct** | Cost Insights requires: (1) **Fusion engine enabled** and (2) **state-aware orchestration enabled**. Both conditions must be met. Additionally, Cost Insights data refreshes with up to a **24-hour lag** — it is not a real-time billing dashboard. Snowflake costs are calculated as credits × price per credit; BigQuery as TiB processed × price (cached = $0); Databricks as proportional DBU allocation. |
> | **C) ❌ Incorrect** | No separate support engagement is required. Cost Insights is self-serve once Fusion and state-aware orchestration are enabled. |
> | **D) ❌ Incorrect** | Cost Insights supports Snowflake, BigQuery, and Databricks — not BigQuery exclusively. |
>
> > 💡 **Key rule**: Cost Insights = **Fusion engine + state-aware orchestration** required. Up to 24-hour refresh lag — not real-time.

---

### Q15.
> **Subdomain 8.15 — Cost formulas by platform**

An architect is setting up Cost Insights for a multi-cloud team using Snowflake and BigQuery. Which cost calculation formulas are correct for each platform?

- A) Snowflake: TiB processed × price per TiB. BigQuery: credits × price per credit.
- B) Snowflake: credits × price per credit. BigQuery: TiB of data processed × price per TiB (cached queries = $0).
- C) Both platforms use credits × price per credit — Cost Insights normalizes across platforms.
- D) Snowflake: warehouse-hours × rate. BigQuery: slot usage × rate.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This reverses the formulas for each platform. |
> | **B) ✅ Correct** | **Snowflake**: cost = **credits × price per credit** (Snowflake charges in virtual warehouse credits). **BigQuery**: cost = **TiB of data processed × price per TiB** — and importantly, **cached queries cost $0** in BigQuery (no data scanned = no charge). **Databricks**: cost is proportional DBU allocation based on query runtime. Each platform has a fundamentally different billing model, and Cost Insights translates these into comparable cost estimates per model run. |
> | **C) ❌ Incorrect** | Cost Insights uses each platform's native billing model — it does not normalize to a single unit. |
> | **D) ❌ Incorrect** | Warehouse-hours and slot usage are not the documented Cost Insights formulas. |
>
> > 💡 **Key rule**: Snowflake = credits × price. BigQuery = TiB processed × price (cached = $0). Databricks = proportional DBU allocation.

---

### Q16.
> **Subdomain 8.16 — Query History: what it tracks**

A data engineer enables Model Query History in dbt Catalog to understand how often their models are queried. They notice that dbt's own model build runs (when dbt materializes tables) are NOT counted in the query history. Is this expected, and why?

- A) Unexpected — all SELECT queries against a model, including dbt builds, should be counted.
- B) Expected — Model Query History tracks **consumption queries** (SELECT queries by downstream users and tools) only. dbt model builds and test executions are explicitly excluded.
- C) Expected — Query History only counts queries executed from the dbt Cloud IDE, not from automated jobs.
- D) Unexpected — dbt builds appear in the 24-hour delayed refresh, not the real-time view.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt build runs are explicitly excluded from Query History counts. |
> | **B) ✅ Correct** | Model Query History is specifically designed to track **consumption** — SELECT queries by **downstream users and BI tools** against production models. It explicitly **excludes dbt model builds and dbt test executions**. This is intentional: the goal is to understand how often business users and tools are consuming the data, not how often dbt is rebuilding it. Including build runs would inflate counts and obscure actual consumption patterns. |
> | **C) ❌ Incorrect** | Query History counts external consumption queries (BI tools, direct SQL), not just IDE queries. |
> | **D) ❌ Incorrect** | The 24-hour lag applies to Cost Insights, not Query History. And the exclusion of dbt builds is by design, not a timing issue. |
>
> > 💡 **Key rule**: Query History = **consumption queries only** (downstream users/tools). Excludes dbt builds and test executions.

---

### Q17.
> **Subdomain 8.17 — Query History: 4 places to view**

A data platform lead wants to identify the top 10 most-consumed models across their entire project to prioritize optimization work. Where in dbt Catalog can they find this information? **Select TWO correct answers.**

- A) Account Settings → Usage dashboard
- B) Project details → "Most consumed models" performance chart
- C) Lineage graph → apply the **Lenses** overlay for query volume
- D) Job run history → sort by execution count
- E) Environment settings → consumption metrics

> [!success]- Answer & Explanations
> **✅ Correct: B, C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Account Settings does not contain a model consumption dashboard. |
> | **B) ✅ Correct** | **Project details → "Most consumed models"** is one of the four places to view Query History. This performance chart shows the highest-traffic models across the project. |
> | **C) ✅ Correct** | The **Lineage graph with the Lenses overlay set to query volume** color-codes nodes by consumption frequency — immediately showing which models in the DAG are most queried. This is particularly useful for understanding consumption patterns in context of the data pipeline. |
> | **D) ❌ Incorrect** | Job run history shows dbt job execution, not downstream user consumption of model data. |
> | **E) ❌ Incorrect** | Environment settings do not show consumption metrics. |
>
> > 💡 **Key rule**: Query History in 4 places: (1) Project details performance chart, (2) Lineage graph Lenses, (3) Resources list sorted by consumption, (4) Individual model page.

---

### Q18.
> **Subdomain 8.18 — Non-dbt asset ingestion**

A team uses dbt Catalog but also has significant data pipelines built in Apache Spark and Fivetran that feed into their dbt models. They want Catalog to show complete end-to-end lineage including these non-dbt assets. Is this possible?

- A) No — dbt Catalog only shows lineage for dbt models. External assets must be documented separately.
- B) Yes — non-dbt warehouse assets can be ingested into dbt Catalog to provide complete lineage that spans both dbt and non-dbt pipeline components.
- C) Yes — but only Fivetran connectors are supported; Spark pipelines require a separate lineage tool.
- D) Yes — but only on Enterprise+ plan and only for assets in the same warehouse as the dbt project.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt Catalog explicitly supports non-dbt asset ingestion for complete lineage. |
> | **B) ✅ Correct** | **Non-dbt warehouse assets** (tables, views, and pipelines from tools like Spark, Fivetran, Kafka, etc.) can be **ingested into dbt Catalog** to provide complete end-to-end lineage. This allows Catalog to show the full data flow: from raw sources through ingestion pipelines, into dbt transformation layers, and out to consuming BI tools — even when parts of the pipeline are outside dbt. |
> | **C) ❌ Incorrect** | The capability is not limited to Fivetran — it applies to non-dbt assets broadly. |
> | **D) ❌ Incorrect** | Non-dbt asset ingestion is not restricted to a specific plan tier or same-warehouse requirement. |
>
> > 💡 **Key rule**: dbt Catalog supports non-dbt asset ingestion for complete end-to-end lineage beyond dbt models.

---

### Q19.
> **Subdomain 8.19 — Staging environment Catalog updates**

A team assumes that only their Production environment deployment job updates dbt Catalog. They set up a Staging environment with its own deployment job for pre-production validation. Will the Staging environment's models appear in Catalog?

- A) No — only the Production environment updates Catalog by definition.
- B) Yes — deployment jobs in **both Production and Staging** environments update Catalog metadata.
- C) Yes — but only if the Staging environment is explicitly linked to Catalog in Account Settings.
- D) No — Staging environments are for validation only and are never reflected in Catalog.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Staging environment deployment jobs also update Catalog. Production is the primary view, but Staging is included. |
> | **B) ✅ Correct** | dbt Catalog is updated by **deployment jobs in both Production and Staging environments** — not just Production. The Staging environment has its own independent view in Catalog (not just a snapshot of Production), allowing pre-production models to be explored and validated before they graduate to Production. CI jobs remain excluded — only scheduled/manual deployment jobs update Catalog. |
> | **C) ❌ Incorrect** | No explicit Catalog linking is required for Staging environments — deployment jobs in Staging automatically update Catalog. |
> | **D) ❌ Incorrect** | Staging environments are reflected in Catalog. The exclusion applies to CI jobs and dev schemas, not Staging environments. |
>
> > 💡 **Key rule**: Catalog updated by deployment jobs in **Production AND Staging** environments. CI jobs and dev schemas are excluded.

---

### Q20.
> **Subdomain 8.20 — Query History use cases**

An architect has enabled Model Query History in dbt Catalog. Which of the following are **valid use cases** for Query History data? **Select TWO correct answers.**

- A) Identifying models to prioritize for performance optimization (high-traffic models benefit most from optimization)
- B) Tracking which dbt developers are most active in running jobs
- C) Assessing the downstream impact before deprecating a model (understanding how many consumers would be affected)
- D) Monitoring dbt job execution duration over time
- E) Comparing the compute cost of two different model materializations

> [!success]- Answer & Explanations
> **✅ Correct: A, C**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | **Optimization prioritization** is a primary use case. High-traffic models (queried frequently by downstream users) deliver the most value when optimized — Query History reveals which models to tackle first for maximum impact. |
> | **B) ❌ Incorrect** | Query History tracks external user/tool consumption of models, not dbt developer activity within dbt Cloud jobs. Developer activity is tracked in dbt Cloud audit logs. |
> | **C) ✅ Correct** | **Deprecation impact assessment** is a primary use case. Before deprecating a model, teams use Query History to understand how many downstream users and tools actively query it, quantifying the migration effort and stakeholder communication needed. |
> | **D) ❌ Incorrect** | Job execution duration is tracked in the dbt Cloud job run history, not Query History. |
> | **E) ❌ Incorrect** | Compute cost comparison uses Cost Insights, not Query History. These are separate features. |
>
> > 💡 **Key rule**: Query History use cases: (1) **optimization prioritization** (which models to improve), (2) **deprecation impact assessment** (who consumes this model).

---

### Q21. ⭐
> **Subdomain 8.21 — Picking the right Lens for a diagnostic workflow**

A platform architect gets a complaint that the warehouse bill spiked last month. They open dbt Catalog and want to narrow in on models that are both (a) frequently queried by downstream consumers and (b) materialized as full-refresh tables rather than incremental. What is the most efficient workflow using Lenses, and what is a common misconception about what Lenses can answer directly?

- A) Apply the **Cost lens** — it directly reports per-model warehouse spend, which already accounts for query volume and materialization strategy. No other lens is needed.
- B) Apply the **Consumption query history lens** first to surface hot nodes, then toggle to the **Materialization type lens** on the same DAG view to spot which hot nodes are `table` vs `incremental`. Lenses do not *combine* overlays simultaneously — you switch between them on the same graph.
- C) Apply the **Test status lens** — degraded tests correlate with expensive rebuilds, so this is the standard cost-triage entry point.
- D) Lenses cannot answer this. You must export the manifest and run_results to an external BI tool because Catalog does not expose query volume or materialization at the node level.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | **There is no "Cost lens"** in dbt Catalog. The available lenses are Resource type, Materialization type, Latest status, Model layer, Test status, and Consumption query history. Cost data lives in **Cost Insights** — a separate Catalog feature that requires the Fusion engine and state-aware orchestration; it is not surfaced as a lens overlay. This is a common trap distractor. |
> | **B) ✅ Correct** | Lenses are **single-attribute overlays** applied one at a time to the same lineage graph. The documented workflow is to switch lenses on the same DAG: **Consumption query history** highlights hot nodes visually, then flipping to **Materialization type** re-colors those same nodes by table/view/incremental/ephemeral. The architect reads the intersection visually. There is no "combined lens" view — that's the common misconception. |
> | **C) ❌ Incorrect** | Test status reflects data quality (worst-case test result per node), not cost or consumption. There's no documented correlation between failing tests and cost spikes. |
> | **D) ❌ Incorrect** | Both **Consumption query history** and **Materialization type** are first-class lenses in dbt Catalog — no external export required. |
>
> > 💡 **Key rule**: Lenses = **one attribute at a time** overlayed on the lineage graph. For multi-attribute diagnostics, switch lenses on the same view and read the intersection visually. The six available lenses: **Resource type, Materialization type, Latest status, Model layer, Test status, Consumption query history**. Cost is *not* a lens — Cost Insights is a separate feature.

---

### Q22. ⭐
> **Subdomain 8.22 — Lens names and definitions**

A new architect on the team is learning the dbt Catalog Lenses system. They want to confirm which Lens corresponds to which behavior. Match the Lens to its definition. **Select TWO correct statements.**

- A) The **Test status** lens shows the status from the latest test execution against a resource. When a model has multiple tests with different results, the lens reflects the **worst-case** status.
- B) The **Latest status** lens shows the result of the model's most recent **test execution** in the current environment.
- C) The **Resource type** lens organizes resources by type (models, tests, seeds, saved query, etc.) and uses the `resource_type` selector.
- D) The **Cost** lens displays warehouse spend per model, color-coded by cost tier. It is one of the six standard lenses in dbt Catalog.
- E) The **Model layer** lens classifies models as `public`, `protected`, or `private` based on their cross-project access modifier.

> [!success]- Answer & Explanations
> **✅ Correct: A, C**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The **Test status** lens reflects the latest test execution against the resource. The documented behavior for models with multiple tests of differing results is that the lens shows the **worst-case** status — a single failing test will color the node `degraded` even if other tests on the same model passed. This protects against false-positive "healthy" coloring. |
> | **B) ❌ Incorrect** | This describes Test status, not Latest status. The **Latest status** lens shows the status from the resource's **latest execution** (the model's own run/build status — success, fail, error, etc.) in the current environment, not its test results. The two lenses are independent. |
> | **C) ✅ Correct** | The **Resource type** lens organizes resources by type — models, tests, seeds, saved queries, sources, exposures, etc. It is backed by the same `resource_type` selector used at the CLI (`--select resource_type:test`). |
> | **D) ❌ Incorrect** | **There is no Cost lens.** Cost data lives in **Cost Insights**, a separate Catalog feature that requires the Fusion engine and state-aware orchestration. The six available lenses are: Resource type, Materialization type, Latest status, Model layer, Test status, Consumption query history. |
> | **E) ❌ Incorrect** | The **Model layer** lens classifies models by **modeling-best-practices layer** (staging / intermediate / marts), based on file prefix or directory — not by cross-project `access` modifier. Access levels (private/protected/public) are not exposed as a lens. |
>
> > 💡 **Key rule**: Six lenses — **Resource type, Materialization type, Latest status, Model layer, Test status, Consumption query history**. Test status uses **worst-case** when multiple tests disagree. Latest status ≠ Test status. There is no Cost lens.

---

### Q23. ⭐
> **Subdomain 8.23 — Model layer lens detection rules**

A team's repository has the following models. Using the **Model layer** Lens in dbt Catalog, which layer would each be classified as?

- `models/marts/finance/fct_orders.sql`
- `models/intermediate/int_order_payments_joined.sql`
- `models/staging/stripe/stg_stripe__charges.sql`
- `models/utils/dim_calendar.sql` (note: not in a `marts/` subdirectory; uses `dim_` prefix)
- `models/cleanup/orders_cleaned.sql` (no recognized prefix, no recognized directory)

Which of the following correctly describes the Model layer Lens classification rules and how each file would be classified? **Select TWO correct answers.**

- A) The Model layer Lens classifies models using **two signals**: file prefix (`stg_`, `int_`, `fct_`/`dim_`) and directory location (`/staging/`, `/intermediate/` or `/int/`, `/marts/`). Either signal alone is sufficient for a layer match.
- B) `fct_orders.sql` → Marts; `int_order_payments_joined.sql` → Intermediate; `stg_stripe__charges.sql` → Staging; `dim_calendar.sql` → **Marts** (the `dim_` prefix matches the Marts rule even though it's not in a `marts/` directory).
- C) `dim_calendar.sql` is classified as **Intermediate** because it's not in a `marts/` directory — directory location takes precedence over prefix.
- D) `orders_cleaned.sql` (no recognized prefix or directory) is automatically classified as **Marts** — Marts is the default fallback layer.
- E) The Model layer Lens uses model **materialization type** (table vs view) to determine the layer, not naming conventions.

> [!success]- Answer & Explanations
> **✅ Correct: A, B**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Per the dbt docs, the Model layer Lens uses **two equivalent signals** — file **prefix** (`stg_` / `int_` / `fct_` or `dim_`) **OR** directory location (`/staging/` / `/intermediate/` or `/int/` / `/marts/`). Either signal alone is enough to classify the model. This means a `dim_calendar.sql` outside a `/marts/` directory is still classified as Marts via its prefix. |
> | **B) ✅ Correct** | All five mappings here are right: `fct_orders.sql` → Marts (both signals match), `int_order_payments_joined.sql` → Intermediate (both match), `stg_stripe__charges.sql` → Staging (both match), and `dim_calendar.sql` → **Marts** via `dim_` prefix despite not being in `/marts/`. The first three reinforce the dual-signal nature; the fourth is the discriminator. |
> | **C) ❌ Incorrect** | There is no precedence rule favoring directory over prefix — either signal classifies the model. `dim_calendar.sql` matches the Marts rule via its prefix. |
> | **D) ❌ Incorrect** | There is **no default fallback layer**. A model with no recognized prefix and no recognized directory is **unclassified** by the Model layer lens — it does not get a default classification. `orders_cleaned.sql` would simply not be tagged with a layer. |
> | **E) ❌ Incorrect** | The Model layer lens is based on **best-practices naming/directory conventions**, not materialization type. Materialization is a separate lens (Materialization type). |
>
> > 💡 **Key rule**: Model layer = prefix **OR** directory match. **Marts** = `fct_`/`dim_` prefix or `/marts/` dir. **Intermediate** = `int_` prefix or `/int/`/`/intermediate/` dir. **Staging** = `stg_` prefix or `/staging/` dir. No default fallback — unrecognized models are unclassified.

---

*[End of Topic 8 — 23 questions]*

