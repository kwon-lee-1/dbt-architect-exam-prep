# Topic 8: dbt Catalog — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 23 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 8.1 — CI jobs do not update Catalog**

A team runs CI jobs on every pull request and a scheduled deployment job every 24 hours. They notice that the dbt Catalog is not reflecting model changes that landed in CI runs during the day — only overnight changes appear. What is the cause?

- A) The Catalog only updates when `dbt docs generate` is run as a standalone command, not as a checkbox.
- B) CI jobs have a 12-hour delay before Catalog updates reflect their changes.
- C) CI jobs **do not update Catalog metadata** — only deployment jobs (scheduled or manual) in production or staging environments do.
- D) CI jobs update Catalog but only for models that passed all tests.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The job type matters, not the `dbt docs generate` step. dbt v2 jobs refresh Catalog automatically, and CI jobs never update it. |
> | **B) ❌ Incorrect** | There is no delayed Catalog update for CI jobs — they are explicitly excluded from Catalog updates. |
> | **C) ✅ Correct** | CI jobs are explicitly excluded from updating dbt Catalog metadata. Only **deployment jobs** (scheduled or manually triggered) running in production or staging environments update the Catalog. This is by design — CI builds temp schemas that don't represent production state. The team's overnight deployment job is the correct Catalog updater. |
> | **D) ❌ Incorrect** | CI test pass/fail status has no bearing on whether CI jobs update Catalog — they simply don't update it at all. |
>
> > 💡 **Key rule**: CI jobs = **never update Catalog**. Only job runs in a production or staging environment update it.

---

### Q2. ⭐
> **Subdomain 8.2 — Catalog inactivity purge**

A team has a `sandbox` environment in dbt Cloud that runs experimental jobs. The environment hasn't had a successful job run in 4 months. What happens to this environment in dbt Catalog?

- A) The environment is purged after 6 months of inactivity.
- B) The environment is automatically purged from Catalog after 3 months with no job runs.
- C) The environment remains in Catalog indefinitely — only manual deletion removes it.
- D) The environment is flagged as "Inactive" in Catalog but remains visible.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The threshold is **3 months**, not 6 months. |
> | **B) ✅ Correct** | The docs say an environment with **no job runs in the past 3 months** has all its metadata purged. The 4-month inactive `sandbox` environment would already be purged. To prevent it, schedule jobs to run at least once every 3 months. |
> | **C) ❌ Incorrect** | Environments are not retained indefinitely — there is an auto-purge policy. |
> | **D) ❌ Incorrect** | There is no "Inactive" flagging status — inactive environments are fully purged. |
>
> > 💡 **Key rule**: No job runs in **3 months** = environment metadata purged from Catalog. Run a job at least every 3 months.

---

### Q3.
> **Subdomain 8.3 — Column-level lineage limitations**

An Enterprise team is excited about column-level lineage in dbt Catalog. They have a mix of SQL and Python models in their project. For which models will column-level lineage be available?

- A) SQL models only — Python models can't be parsed.
- B) Only models with `contract: enforced: true` — contracts are required for column-level lineage.
- C) All models — column-level lineage works for both SQL and Python models.
- D) Only models using the `table` or `incremental` materialization — views are excluded.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Column-level lineage (Enterprise and Enterprise+) is built from the SQL `select` statements in a model. The docs say it's not possible to parse a Python model, so Catalog shows a Python error for it. |
> | **B) ❌ Incorrect** | Contracts are not a prerequisite for column-level lineage — they are separate concepts. |
> | **C) ❌ Incorrect** | Column-level lineage explicitly does NOT work for Python models regardless of plan. |
> | **D) ❌ Incorrect** | The docs don't limit column-level lineage by materialization. |
>
> > 💡 **Key rule**: Column-level lineage = Enterprise / Enterprise+ AND **SQL models only**. Python models can't be parsed.

---

### Q4.
> **Subdomain 8.4 — What catalog.json contains vs manifest.json**

A data engineer is debugging why the dbt Catalog shows incorrect column types for a model. They need to understand which artifact file to inspect. What does `catalog.json` contain that `manifest.json` does not?

- A) `catalog.json` contains run results and test outcomes; `manifest.json` contains model definitions.
- B) `catalog.json` contains environment variable values; `manifest.json` contains connection details.
- C) `catalog.json` contains the compiled SQL for each model; `manifest.json` contains the raw Jinja.
- D) `catalog.json` contains warehouse metadata about the tables and views your project builds (column names, types, stats); `manifest.json` contains model metadata and lineage from the dbt project.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Run results and test outcomes are in `run_results.json` — not `catalog.json`. |
> | **B) ❌ Incorrect** | Environment variables and connection details are not stored in either `catalog.json` or `manifest.json`. |
> | **C) ❌ Incorrect** | Compiled SQL is in the `target/` directory as individual `.sql` files, or in `manifest.json`'s compiled SQL field — not `catalog.json`. |
> | **D) ✅ Correct** | `catalog.json` contains **warehouse metadata** about the tables and views your project builds: column names, types and stats, as they exist in the warehouse. `manifest.json` contains dbt project metadata: model definitions, lineage graph, configs, node relationships. |
>
> > 💡 **Key rule**: `catalog.json` = **warehouse metadata** (column names, types, stats). `manifest.json` = project metadata and lineage.

---

### Q5.
> **Subdomain 8.5 — Docs step for dbt v2 jobs**

A team runs dbt v2 deployment jobs in their Production environment. Do they need a `dbt docs generate` step for Catalog to refresh?

- A) Yes, every job needs a `dbt docs generate` step.
- B) No. dbt v2 jobs refresh Catalog metadata automatically on every run.
- C) Yes, but only the first job in each project.
- D) No, but only if the job runs on a schedule.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs say you don't need a `dbt docs generate` step with dbt v2. |
> | **B) ✅ Correct** | Jobs on dbt v2 refresh Catalog metadata on every run. Some metadata still needs specific commands: test results need `dbt test` or `dbt build`, and source freshness needs `dbt source freshness`. |
> | **C) ❌ Incorrect** | There's no first-job rule. |
> | **D) ❌ Incorrect** | Scheduled or manual doesn't matter. What matters is a production or staging deployment run. |
>
> > 💡 **Key rule**: dbt v2 jobs update Catalog automatically. Test results need `dbt test`/`build`. Freshness needs `dbt source freshness`.

---

### Q6. ⭐
> **Subdomain 8.6 — Model Query History**

A team wants to use dbt Catalog's Model Query History feature to identify which models are most frequently queried by downstream users, in order to prioritize optimization work. What is required to enable this feature?

- A) Enterprise or Enterprise+ plan, and it must be enabled in the Production environment settings by testing and enabling query history permissions.
- B) Starter plan with the Advanced CI feature enabled.
- C) The feature is available on all dbt Cloud plans — no specific plan required.
- D) Enterprise+ plan only, and it requires the Fusion engine to be enabled.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Model Query History requires **Enterprise or Enterprise+** plan. New PROD environments have it on automatically. For an existing one: Orchestration → Environments → select the Production environment → Settings → scroll to Query History → click **"Test Permissions"** → check **"Enable query history"** → Save. It tracks SELECT queries by downstream users/tools (excludes dbt builds and test runs). |
> | **B) ❌ Incorrect** | Advanced CI and Model Query History are unrelated features. |
> | **C) ❌ Incorrect** | Model Query History is not available on Starter or Developer plans. |
> | **D) ❌ Incorrect** | Query history is available on Enterprise and Enterprise+, and the docs don't require Fusion. |
>
> > 💡 **Key rule**: Model Query History = **Enterprise or Enterprise+**. On by default for new PROD environments. Tracks consumption SELECT queries only (not dbt builds).

---

---

### Q7.
> **Subdomain 8.7 — dbt Docs vs dbt Catalog**

A new team member asks about the difference between `dbt docs generate` (dbt Docs) and dbt Catalog. Which statement is correct?

- A) dbt Docs is available on Enterprise+; dbt Catalog is available on all plans.
- B) dbt Catalog is built on top of `dbt docs generate` artifacts and requires them to be generated daily.
- C) dbt Docs generates a static HTML site from project metadata (available on all plans). dbt Catalog is a dynamic real-time metadata platform (available on Starter+ only) with features like lineage, data health, and query history.
- D) They are the same product — dbt Catalog is just the new branding for dbt Docs.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt Docs is available on all plans; dbt Catalog requires Starter+. This is the reverse of the stated answer. |
> | **B) ❌ Incorrect** | Catalog gets its metadata from job runs through the Discovery API. dbt v2 jobs need no `dbt docs generate` step. |
> | **C) ✅ Correct** | **dbt Docs** (`dbt docs generate`) creates a **static site** from project artifacts that you host yourself. dbt Docs v2 isn't available in the dbt platform. It reflects the state at the time of generation. **dbt Catalog** is a **dynamic, real-time metadata platform** in dbt Cloud that provides lineage, data health signals, and exploration tools on **Starter and above** (query history and column-level lineage need Enterprise tiers). Catalog updates after production and staging job runs; dbt Docs is a point-in-time snapshot. |
> | **D) ❌ Incorrect** | They are distinct products with different capabilities, plans, and use cases. |
>
> > 💡 **Key rule**: dbt Docs = static HTML, all plans. dbt Catalog = dynamic real-time metadata, Starter+ only.

---

### Q8.
> **Subdomain 8.8 — Dev builds don't appear in Catalog**

A developer builds and tests a model in the dbt Cloud IDE in their personal dev schema (`dbt_alice`). They expect to see it appear in dbt Catalog so they can share a lineage link with a stakeholder. The model does not appear in Catalog. Why?

- A) Catalog only indexes models that have been tagged with `+catalog: true` in their config.
- B) Catalog shows **production and staging deployment runs**. Models built only in a developer's dev schema don't appear.
- C) The developer must manually publish the model to Catalog from the IDE using the "Publish" button.
- D) The model needs to be committed to the main branch before it appears in Catalog.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no `catalog: true` tag requirement. Models appear based on job runs in the production or staging environment. |
> | **B) ✅ Correct** | Catalog updates after job runs in the **production or staging** deployment environment. A model built in a developer's personal schema (dev) doesn't appear until a production or staging deployment job builds it. |
> | **C) ❌ Incorrect** | There is no manual "Publish to Catalog" button in the IDE. |
> | **D) ❌ Incorrect** | Committing to main is not sufficient. A production or staging deployment job must run. |
>
> > 💡 **Key rule**: Catalog = production and staging deployment runs. Dev builds are invisible.

---

### Q9.
> **Subdomain 8.9 — Data health signals**

A stakeholder views a model in dbt Catalog and sees a **"Degraded"** health signal. What can cause it?

- A) The model has no description — degraded means undocumented.
- B) The model has not been built in more than 30 days.
- C) The model failed to build, has failing tests, or an upstream source is stale.
- D) The model has more than 100 downstream consumers.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | A missing description gives **Caution**, not Degraded. |
> | **B) ❌ Incorrect** | Not built in 30 days gives **Caution**, not Degraded. |
> | **C) ✅ Correct** | Degraded for a model = failed to build, failing tests, or a stale upstream source (freshness errored or hasn't run in 30 days). |
> | **D) ❌ Incorrect** | Consumer count isn't a health signal. |
>
> > 💡 **Key rule**: Statuses: Healthy / Caution / Degraded / **Unknown** (no run has processed it). **Caution** = warnings, no tests, no description, not built in 30 days. **Degraded** = failures or stale sources. Available on all plans (Preview).

---

### Q10.
> **Subdomain 8.10 — Lenses DAG overlays**

A data platform team wants to quickly identify which models in the lineage graph have the most test failures and which are materialized as views vs tables. Which dbt Catalog feature allows this?

- A) The **Lenses** feature — DAG overlays that color-code nodes by attributes like materialization type, test status, model layer, or consumption query history.
- B) The **Filters** panel — allows filtering models by materialization type and test status.
- C) The **Resources** tab — lists all models with sortable columns for materialization and test status.
- D) The **Column-level lineage** view — shows test status per column in the lineage graph.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | **Lenses** are visual **DAG overlays** in dbt Catalog's lineage graph. They color-code nodes based on selected attributes. Per the dbt docs, the available lenses are: **Resource type**, **Materialization type**, **Latest status**, **Model layer** (staging / intermediate / marts), **Test status**, and **Consumption query history**. This allows rapid visual identification of problem areas, materialization patterns, or hot/cold consumption directly in the graph. |
> | **B) ❌ Incorrect** | Filters narrow which nodes are shown; they don't provide a visual DAG overlay. |
> | **C) ❌ Incorrect** | The Resources tab is a list view — useful for sorting, but does not provide the visual DAG overlay that Lenses provide. |
> | **D) ❌ Incorrect** | Column-level lineage shows column data flow, not test status overlays on nodes. |
>
> > 💡 **Key rule**: Lenses = DAG overlays in dbt Catalog. Six lenses available: Resource type, Materialization type, Latest status, Model layer, Test status, Consumption query history. **Cost is NOT a lens** — Cost Insights is a separate Catalog feature.

---

### Q11.
> **Subdomain 8.11 — Cross-project lineage requirements**

A governance lead wants Catalog lineage that spans multiple dbt projects. What does the setup need?

- A) Enterprise or Enterprise+, public models in the upstream project, and project dependencies in the downstream project.
- B) Any plan, with `dbt docs generate` in each project.
- C) Enterprise+ only.
- D) The Starter plan with dbt Mesh configured.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Multi-project lineage is on Enterprise and Enterprise+. It shows public models, and a project appears as a dependent when it lists the upstream in `dependencies.yml`. |
> | **B) ❌ Incorrect** | A docs step doesn't create cross-project lineage. |
> | **C) ❌ Incorrect** | Enterprise has it too. |
> | **D) ❌ Incorrect** | Project dependencies and multi-project lineage aren't on Starter. |
>
> > 💡 **Key rule**: Multi-project lineage = **Enterprise / Enterprise+**, public models + project dependencies. Direct references only.

---

### Q12.
> **Subdomain 8.12 — Artifacts setting**

A team has four deployment jobs. An admin opens Account settings → project → Edit → **Artifacts**. What does this setting do?

- A) It decides which job Catalog reads. Designate all four.
- B) It picks the job whose artifacts feed legacy dbt Docs and source freshness links. Catalog reads metadata from the Discovery API after each production or staging run. Associate only one production job.
- C) It's a per-job "Publish to Catalog" toggle.
- D) It's a "Catalog source job" dropdown in the Production environment settings.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Catalog doesn't use this setting. The docs say to associate only one production job with a project. |
> | **B) ✅ Correct** | The Artifacts setting is labeled legacy dbt Docs. Catalog refreshes after each production or staging run. |
> | **C) ❌ Incorrect** | There's no such toggle. |
> | **D) ❌ Incorrect** | There's no such dropdown. |
>
> > 💡 **Key rule**: Account settings → project → Edit → Artifacts = legacy dbt Docs / freshness. One production job per project. Catalog doesn't depend on it.

---

### Q13.
> **Subdomain 8.13 — sources.json contents**

An architect is auditing what each dbt artifact file contains. What information is stored in `sources.json` that is NOT in `manifest.json`?

- A) Source table names and their warehouse locations
- B) Source-to-model lineage edges
- C) Source schema definitions and column names
- D) **Source freshness check results** — the actual freshness measurements and pass/fail status from the last `dbt source freshness` run

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Source table names and locations are defined in the project YAML and appear in `manifest.json` as source node metadata. |
> | **B) ❌ Incorrect** | Source-to-model lineage is captured in `manifest.json` as part of the project DAG. |
> | **C) ❌ Incorrect** | Source schema definitions (column names, descriptions) are in `manifest.json`. |
> | **D) ✅ Correct** | `sources.json` contains **source definitions AND freshness check results** — specifically the actual freshness measurements (e.g., time since last update) and the pass/warn/error status from `dbt source freshness` runs. `manifest.json` contains the source definitions but not the runtime freshness results. This is why `sources.json` must be refreshed regularly to reflect current data freshness state in Catalog. |
>
> > 💡 **Key rule**: `sources.json` = source definitions + **freshness check results** (actual measured freshness + pass/warn/error status). `manifest.json` = project structure, lineage, metadata.

---

### Q14.
> **Subdomain 8.14 — Cost Insights requirements**

A team on Enterprise wants Cost Insights for Snowflake spend per model. What does it need?

- A) The Fusion engine and state-aware orchestration, both required.
- B) A supported warehouse, platform metadata credentials with a passing test, and at least one production job. State-aware orchestration or dbt State is only needed for cost-reduction data.
- C) A separate Snowflake integration set up by dbt support.
- D) BigQuery only. Snowflake isn't supported.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs don't list Fusion as a requirement. State-aware orchestration is only for reduction data. |
> | **B) ✅ Correct** | Cost Insights is on Enterprise and Enterprise+. Cost data appears after production jobs run. |
> | **C) ❌ Incorrect** | Not required. |
> | **D) ❌ Incorrect** | Supported: Snowflake, BigQuery, Databricks, Redshift (Preview). |
>
> > 💡 **Key rule**: Cost Insights = Enterprise / Enterprise+, metadata credentials, production job. Refreshes once daily. Estimates, not billing reconciliation.

---

### Q15.
> **Subdomain 8.15 — Cost formulas by platform**

An architect is setting up Cost Insights for a multi-cloud team using Snowflake and BigQuery. Which cost calculation formulas are correct for each platform?

- A) Snowflake: TiB processed × price per TiB. BigQuery: credits × price per credit.
- B) Both platforms use credits × price per credit — Cost Insights normalizes across platforms.
- C) Snowflake: credits × price per credit. BigQuery: TiB of data processed × price per TiB (cached queries = $0).
- D) Snowflake: warehouse-hours × rate. BigQuery: slot usage × rate.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This reverses the formulas for each platform. |
> | **B) ❌ Incorrect** | Cost Insights uses each platform's native billing model — it does not normalize to a single unit. |
> | **C) ✅ Correct** | **Snowflake**: cost = **credits × price per credit** (Snowflake charges in virtual warehouse credits). **BigQuery** (on-demand): cost = **TiB processed × price per TiB**. Capacity pricing uses slot-hours instead. Cached queries are $0. **Databricks**: cost is proportional DBU allocation based on query runtime. Each platform has a fundamentally different billing model, and Cost Insights translates these into comparable cost estimates per model run. |
> | **D) ❌ Incorrect** | Snowflake isn't costed by warehouse-hours. Slot-hours is BigQuery capacity pricing only. |
>
> > 💡 **Key rule**: Snowflake = credits × price. BigQuery on-demand = TiB processed × price per TiB (capacity = slot hours; cached = $0). Databricks = proportional DBU allocation.

---

### Q16.
> **Subdomain 8.16 — Query History: what it tracks**

A data engineer enables Model Query History in dbt Catalog to understand how often their models are queried. They notice that dbt's own model build runs (when dbt materializes tables) are NOT counted in the query history. Is this expected, and why?

- A) Expected — Model Query History tracks **consumption queries** (SELECT queries by downstream users and tools) only. dbt model builds and test executions are explicitly excluded.
- B) Unexpected — dbt builds appear in the 24-hour delayed refresh, not the real-time view.
- C) Unexpected — all SELECT queries against a model, including dbt builds, should be counted.
- D) Expected — Query History only counts queries executed from the dbt Cloud IDE, not from automated jobs.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Model Query History is specifically designed to track **consumption** — SELECT queries by **downstream users and BI tools** against production models. It explicitly **excludes dbt model builds and dbt test executions**. This is intentional: the goal is to understand how often business users and tools are consuming the data, not how often dbt is rebuilding it. Including build runs would inflate counts and obscure actual consumption patterns. |
> | **B) ❌ Incorrect** | The exclusion of dbt builds is by design, not a timing issue. |
> | **C) ❌ Incorrect** | dbt build runs are explicitly excluded from Query History counts. |
> | **D) ❌ Incorrect** | Query History counts external consumption queries (BI tools, direct SQL), not just IDE queries. |
>
> > 💡 **Key rule**: Query History = **consumption queries only** (downstream users/tools). Excludes dbt builds and test executions.

---

### Q17.
> **Subdomain 8.17 — Query History: 4 places to view**

A data platform lead wants to identify the top 10 most-consumed models across their entire project to prioritize optimization work. Where in dbt Catalog can they find this information? **Select TWO correct answers.**

- A) Environment settings → consumption metrics
- B) Account Settings → Usage dashboard
- C) Lineage graph → apply the **Lenses** overlay for query volume
- D) Project details → "Most consumed models" performance chart
- E) Job run history → sort by execution count

> [!success]- Answer & Explanations
> **✅ Correct: C, D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Environment settings do not show consumption metrics. |
> | **B) ❌ Incorrect** | Account Settings does not contain a model consumption dashboard. |
> | **C) ✅ Correct** | The **Lineage graph with the Lenses overlay set to query volume** color-codes nodes by consumption frequency — immediately showing which models in the DAG are most queried. This is particularly useful for understanding consumption patterns in context of the data pipeline. |
> | **D) ✅ Correct** | **Project details → "Most consumed models"** is one of the four places to view Query History. This performance chart shows the highest-traffic models across the project. |
> | **E) ❌ Incorrect** | Job run history shows dbt job execution, not downstream user consumption of model data. |
>
> > 💡 **Key rule**: Query History in 4 places: (1) Project details performance chart, (2) Lineage graph Lenses, (3) Resources list sorted by consumption, (4) Individual model page.

---

### Q18.
> **Subdomain 8.18 — External metadata ingestion**

A team wants Catalog to show Snowflake tables and views that aren't defined in dbt. What is available?

- A) External metadata ingestion (Preview) on Enterprise and Enterprise+. Snowflake only for now.
- B) It's available on all plans and all warehouses.
- C) Catalog only ever shows dbt resources.
- D) Only Fivetran connectors are supported.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | It connects to the warehouse so Catalog can show resources not defined in dbt. It runs daily at 5 PM UTC and when you save credentials. |
> | **B) ❌ Incorrect** | Enterprise tiers only, and Snowflake only for now. |
> | **C) ❌ Incorrect** | Ingestion exists for non-dbt warehouse resources. |
> | **D) ❌ Incorrect** | It reads the warehouse, not specific tools. |
>
> > 💡 **Key rule**: External metadata ingestion = Enterprise / Enterprise+, Preview, Snowflake only.

---

### Q19.
> **Subdomain 8.19 — Staging environment Catalog updates**

A team assumes that only their Production environment deployment job updates dbt Catalog. They set up a Staging environment with its own deployment job for pre-production validation. Will the Staging environment's models appear in Catalog?

- A) No — Staging environments are for validation only and are never reflected in Catalog.
- B) Yes — deployment jobs in **both Production and Staging** environments update Catalog metadata.
- C) Yes — but only if the Staging environment is explicitly linked to Catalog in Account Settings.
- D) No — only the Production environment updates Catalog by definition.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Staging environments are reflected in Catalog. The exclusion applies to CI jobs and dev schemas, not Staging environments. |
> | **B) ✅ Correct** | dbt Catalog is updated by **deployment jobs in both Production and Staging environments** — not just Production. Set a single environment per project as production or staging. CI jobs remain excluded. |
> | **C) ❌ Incorrect** | No explicit Catalog linking is required for Staging environments — deployment jobs in Staging automatically update Catalog. |
> | **D) ❌ Incorrect** | Staging environment deployment jobs also update Catalog. Production is the primary view, but Staging is included. |
>
> > 💡 **Key rule**: Catalog updated by deployment jobs in **Production AND Staging** environments. CI jobs and dev schemas are excluded.

---

### Q20.
> **Subdomain 8.20 — Query History use cases**

An architect has enabled Model Query History in dbt Catalog. Which of the following are **valid use cases** for Query History data? **Select TWO correct answers.**

- A) Identifying models to prioritize for performance optimization (high-traffic models benefit most from optimization)
- B) Tracking which dbt developers are most active in running jobs
- C) Comparing the compute cost of two different model materializations
- D) Monitoring dbt job execution duration over time
- E) Assessing the downstream impact before deprecating a model (understanding how many consumers would be affected)

> [!success]- Answer & Explanations
> **✅ Correct: A, E**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | **Optimization prioritization** is a primary use case. High-traffic models (queried frequently by downstream users) deliver the most value when optimized — Query History reveals which models to tackle first for maximum impact. |
> | **B) ❌ Incorrect** | Query History tracks external user/tool consumption of models, not dbt developer activity within dbt Cloud jobs. Developer activity is tracked in dbt Cloud audit logs. |
> | **C) ❌ Incorrect** | Compute cost comparison uses Cost Insights, not Query History. These are separate features. |
> | **D) ❌ Incorrect** | Job execution duration is tracked in the dbt Cloud job run history, not Query History. |
> | **E) ✅ Correct** | **Deprecation impact assessment** is a primary use case. Before deprecating a model, teams use Query History to understand how many downstream users and tools actively query it, quantifying the migration effort and stakeholder communication needed. |
>
> > 💡 **Key rule**: Query History use cases: (1) **optimization prioritization** (which models to improve), (2) **deprecation impact assessment** (who consumes this model).

---

### Q21. ⭐
> **Subdomain 8.21 — Picking the right Lens for a diagnostic workflow**

A platform architect gets a complaint that the warehouse bill spiked last month. They open dbt Catalog and want to narrow in on models that are both (a) frequently queried by downstream consumers and (b) materialized as full-refresh tables rather than incremental. What is the most efficient workflow using Lenses, and what is a common misconception about what Lenses can answer directly?

- A) Apply the **Cost lens** — it directly reports per-model warehouse spend, which already accounts for query volume and materialization strategy. No other lens is needed.
- B) Lenses cannot answer this. You must export the manifest and run_results to an external BI tool because Catalog does not expose query volume or materialization at the node level.
- C) Apply the **Consumption query history lens** first to surface hot nodes, then toggle to the **Materialization type lens** on the same DAG view to spot which hot nodes are `table` vs `incremental`. Lenses do not *combine* overlays simultaneously — you switch between them on the same graph.
- D) Apply the **Test status lens** — degraded tests correlate with expensive rebuilds, so this is the standard cost-triage entry point.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | **There is no "Cost lens"** in dbt Catalog. The available lenses are Resource type, Materialization type, Latest status, Model layer, Test status, and Consumption query history. Cost data lives in **Cost Insights**, a separate feature (Enterprise / Enterprise+). It isn't a lens. This is a common trap distractor. |
> | **B) ❌ Incorrect** | Both **Consumption query history** and **Materialization type** are first-class lenses in dbt Catalog — no external export required. |
> | **C) ✅ Correct** | Lenses are **single-attribute overlays** applied one at a time to the same lineage graph. The documented workflow is to switch lenses on the same DAG: **Consumption query history** highlights hot nodes visually, then flipping to **Materialization type** re-colors those same nodes by table/view/incremental/ephemeral. The architect reads the intersection visually. There is no "combined lens" view — that's the common misconception. |
> | **D) ❌ Incorrect** | Test status reflects data quality (worst-case test result per node), not cost or consumption. There's no documented correlation between failing tests and cost spikes. |
>
> > 💡 **Key rule**: Lenses = **one attribute at a time** overlayed on the lineage graph. For multi-attribute diagnostics, switch lenses on the same view and read the intersection visually. The six available lenses: **Resource type, Materialization type, Latest status, Model layer, Test status, Consumption query history**. Cost is *not* a lens — Cost Insights is a separate feature.

---

### Q22. ⭐
> **Subdomain 8.22 — Lens names and definitions**

A new architect on the team is learning the dbt Catalog Lenses system. They want to confirm which Lens corresponds to which behavior. Match the Lens to its definition. **Select TWO correct statements.**

- A) The **Test status** lens shows the status from the latest test execution against a resource. When a model has multiple tests with different results, the lens reflects the **worst-case** status.
- B) The **Latest status** lens shows the result of the model's most recent **test execution** in the current environment.
- C) The **Model layer** lens classifies models as `public`, `protected`, or `private` based on their cross-project access modifier.
- D) The **Cost** lens displays warehouse spend per model, color-coded by cost tier. It is one of the six standard lenses in dbt Catalog.
- E) The **Resource type** lens organizes resources by type (models, tests, seeds, saved query, etc.) and uses the `resource_type` selector.

> [!success]- Answer & Explanations
> **✅ Correct: A, E**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The **Test status** lens reflects the latest test execution against the resource. The documented behavior for models with multiple tests of differing results is that the lens shows the **worst-case** status — a single failing test will color the node `degraded` even if other tests on the same model passed. This protects against false-positive "healthy" coloring. |
> | **B) ❌ Incorrect** | This describes Test status, not Latest status. The **Latest status** lens shows the status from the resource's **latest execution** (the model's own run/build status — success, fail, error, etc.) in the current environment, not its test results. The two lenses are independent. |
> | **C) ❌ Incorrect** | The **Model layer** lens classifies models by **modeling-best-practices layer** (staging / intermediate / marts), based on file prefix or directory — not by cross-project `access` modifier. Access levels (private/protected/public) are not exposed as a lens. |
> | **D) ❌ Incorrect** | **There is no Cost lens.** Cost data lives in **Cost Insights**, a separate feature (Enterprise / Enterprise+). The six available lenses are: Resource type, Materialization type, Latest status, Model layer, Test status, Consumption query history. |
> | **E) ✅ Correct** | The **Resource type** lens organizes resources by type — models, tests, seeds, saved queries, sources, exposures, etc. It is backed by the same `resource_type` selector used at the CLI (`--select resource_type:test`). |
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
- D) The Model layer Lens uses model **materialization type** (table vs view) to determine the layer, not naming conventions.
- E) `orders_cleaned.sql` (no recognized prefix or directory) is automatically classified as **Marts** — Marts is the default fallback layer.

> [!success]- Answer & Explanations
> **✅ Correct: A, B**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Per the dbt docs, the Model layer Lens uses **two equivalent signals** — file **prefix** (`stg_` / `int_` / `fct_` or `dim_`) **OR** directory location (`/staging/` / `/intermediate/` or `/int/` / `/marts/`). Either signal alone is enough to classify the model. This means a `dim_calendar.sql` outside a `/marts/` directory is still classified as Marts via its prefix. |
> | **B) ✅ Correct** | All five mappings here are right: `fct_orders.sql` → Marts (both signals match), `int_order_payments_joined.sql` → Intermediate (both match), `stg_stripe__charges.sql` → Staging (both match), and `dim_calendar.sql` → **Marts** via `dim_` prefix despite not being in `/marts/`. The first three reinforce the dual-signal nature; the fourth is the discriminator. |
> | **C) ❌ Incorrect** | There is no precedence rule favoring directory over prefix — either signal classifies the model. `dim_calendar.sql` matches the Marts rule via its prefix. |
> | **D) ❌ Incorrect** | The Model layer lens is based on **best-practices naming/directory conventions**, not materialization type. Materialization is a separate lens (Materialization type). |
> | **E) ❌ Incorrect** | There is **no default fallback layer**. A model with no recognized prefix and no recognized directory is **unclassified** by the Model layer lens — it does not get a default classification. `orders_cleaned.sql` would simply not be tagged with a layer. |
>
> > 💡 **Key rule**: Model layer = prefix **OR** directory match. **Marts** = `fct_`/`dim_` prefix or `/marts/` dir. **Intermediate** = `int_` prefix or `/int/`/`/intermediate/` dir. **Staging** = `stg_` prefix or `/staging/` dir. No default fallback — unrecognized models are unclassified.

---

*[End of Topic 8 — 23 questions]*

