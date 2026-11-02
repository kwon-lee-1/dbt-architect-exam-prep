# Topic 10: dbt Commands & Node Selection — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 21 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 10.1 — `@` graph operator vs `+model+`**

A data engineer wants to run `model_x` and all of its descendants, but also wants to ensure that every ancestor of every descendant is included so that the full graph is self-consistent. Which selector achieves this?

- A) `@model_x`
- B) `+model_x+`
- C) `model_x*`
- D) `model_x+`

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | `@model_x` is the **full closure operator**. It expands to: `model_x` + all descendants of `model_x` + all ancestors of every one of those descendants. Use it when you need a complete, self-contained subgraph — everything needed to rebuild `model_x` and validate all downstream consumers. |
> | **B) ❌ Incorrect** | `+model_x+` = all ancestors of `model_x` **plus** all descendants of `model_x`. It does NOT include ancestors of the descendants — only ancestors of `model_x` itself. |
> | **C) ❌ Incorrect** | `model_x*` is not valid dbt selector syntax. |
> | **D) ❌ Incorrect** | `model_x+` = `model_x` and all its descendants, but none of their ancestors. |
>
> > 💡 **Key rule**: `@model` = model + descendants + **all ancestors of descendants**. `+model+` = model's own ancestors + model + model's own descendants. The `@` operator is uniquely needed for full-closure subgraph runs.

---

### Q2. ⭐
> **Subdomain 10.2 — Set operator: union vs intersection**

A CI job needs to run only models that are both modified AND tagged `nightly`. Which dbt selector syntax correctly expresses this intersection?

- A) `state:modified tag:nightly`
- B) `state:modified,tag:nightly`
- C) `state:modified & tag:nightly`
- D) `state:modified+tag:nightly`

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | A **space** between selectors = **union**. This runs models that are modified OR tagged `nightly` (whichever set is larger). |
> | **B) ✅ Correct** | A **comma** between selectors = **intersection**. `state:modified,tag:nightly` selects only the nodes that satisfy BOTH conditions simultaneously. This is the correct syntax for "modified AND tagged". |
> | **C) ❌ Incorrect** | The docs don't mention `&`. Intersection is a comma. |
> | **D) ❌ Incorrect** | The `+` attached to a selector adds graph depth (parents/children), not set intersection. This is invalid for combining two different selectors. |
>
> > 💡 **Key rule**: **Space = union** (either/or). **Comma = intersection** (both/and). This is one of the most commonly confused distinctions in dbt node selection.

---

### Q3. ⭐
> **Subdomain 10.3 — `state:modified` and `var()` / `env_var()`**

A team uses CI slim builds with `dbt run --select state:modified+ --state ./prod-manifest`. They find that changing the value of a variable used in a model with `{{ var('some_var') }}` doesn't flag the model as modified. Why?

- A) The `--state` flag must be combined with `--vars` for variable changes to be tracked.
- B) `state:modified` compares compiled SQL, so any variable change would be detected.
- C) dbt can't trace a `var()` or `env_var()` value change into `state:modified`. The model is likely flagged only if the change alters its configuration.
- D) Variable changes are detected only with `state:modified.configs`, not `state:modified`.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Passing `--vars` with `--state` doesn't change this. |
> | **B) ❌ Incorrect** | The docs say dbt can't identify that lineage, so the model isn't included just because the value changed. |
> | **C) ✅ Correct** | The state comparison caveats page says dbt is unable to include the model in `state:modified` because a `var` or `env_var` value changed. It's likely marked modified only if the change results in a different configuration. |
> | **D) ❌ Incorrect** | Not documented. |
>
> > 💡 **Key rule**: `var()` / `env_var()` value changes aren't traced by `state:modified`. Don't rely on it alone to find affected models.

---

### Q4. ⭐
> **Subdomain 10.4 — Manifest overwrite problem**

A CI pipeline runs `dbt run --select state:modified+ --state ./target --target-path ./target`. The team notices the slim CI always builds every model, not just modified ones. What is the root cause?

- A) When `--state` and `--target-path` point to the same directory, dbt overwrites `manifest.json` during the parse phase before it can be used for comparison.
- B) The `state:modified` selector requires a separate `--profiles-dir` to work correctly.
- C) `--state` and `--target-path` cannot be used together; they are mutually exclusive flags.
- D) `--target-path` must point to an absolute path, not a relative path, for state comparison to work.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say dbt overwrites `manifest.json` during parsing, and warn that setting `--state` and `--target-path` to the same path with `--defer` or `state:modified` can lead to non-idempotent behavior. Fixes: move the manifest to its own folder (for example `state/`), write to a different `--target-path`, or pass `--no-write-json`. |
> | **B) ❌ Incorrect** | `--profiles-dir` is unrelated to state comparison. |
> | **C) ❌ Incorrect** | These flags are not mutually exclusive — but pointing them at the same directory is the bug. |
> | **D) ❌ Incorrect** | Relative vs absolute path is not the issue here. |
>
> > 💡 **Key rule**: **Don't point `--state` and `--target-path` at the same directory.** dbt overwrites `manifest.json` while parsing, which can lead to non-idempotent behavior. Use a separate path like `--state ./prod-manifest`.

---

### Q5. ⭐
> **Subdomain 10.5 — `--defer-state` for split comparison and deferral**

A team wants their CI slim build to compare modified nodes against the **production** manifest, but defer missing relations to the **staging** environment (which has fresher data). Which flag combination achieves this?

- A) This is not possible in dbt; `--state` and deferral must use the same manifest.
- B) Use `--state ./prod-manifest --defer` — dbt automatically defers to the staging environment when relations are missing.
- C) Use `--defer-state ./staging-manifest` alone — this flag handles both comparison and deferral.
- D) Use `--state ./prod-manifest --defer --defer-state ./staging-manifest` — `--state` drives comparison; `--defer-state` drives deferral resolution.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This is exactly the use case `--defer-state` was designed for. |
> | **B) ❌ Incorrect** | `--defer` alone defers to whatever manifest `--state` points to — there is no automatic environment detection. |
> | **C) ❌ Incorrect** | `--defer-state` only controls deferral resolution, not state comparison. `--state` is still required for `state:modified`. |
> | **D) ✅ Correct** | `--defer-state` is a separate flag that lets you specify a **different manifest** for deferral resolution than the one used for `state:modified` comparison. `--state` answers "what changed?" and `--defer-state` answers "where do I find existing relations to defer to?" This is ideal when production is the authoritative baseline but staging has more recent data. |
>
> > 💡 **Key rule**: `--state` = comparison baseline for `state:modified`. `--defer-state` = separate manifest for deferral resolution. They can point to different manifests.

---

### Q6. ⭐
> **Subdomain 10.6 — `--indirect-selection` modes**

You run `dbt test --select model_a`. A `relationships` test references both `model_a` and `model_b`. Which mode restricts tests to those that **exclusively** reference selected nodes, so this test is left out?

- A) `eager` (default)
- B) `cautious`
- C) `buildable`
- D) `empty`

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `eager` is the most inclusive. It runs tests if any parent is selected, even if they also reference unselected nodes. |
> | **B) ✅ Correct** | `cautious` is the most exclusive mode. It restricts tests to those that exclusively reference selected nodes. |
> | **C) ❌ Incorrect** | `buildable` is a middle ground: tests whose references are each within the selected nodes or their ancestors. |
> | **D) ❌ Incorrect** | `empty` runs no tests at all, even ones attached directly to the selected node. |
>
> > 💡 **Key rule**: `eager` = any parent selected. `buildable` = selected nodes or their ancestors. `cautious` = only selected nodes. `empty` = no tests.

---

### Q7. ⭐
> **Subdomain 10.7 — `dbt build` unit test execution order**

A data engineer adds a unit test to `model_x`. When `dbt build` runs, in what order does the unit test execute relative to the model materialization?

- A) Unit tests run before model materialization; data tests run after materialization.
- B) Unit tests and data tests both run after model materialization.
- C) Unit tests run after model materialization, then data tests run last.
- D) Unit tests run at the start of the entire `dbt build` job before any models are materialized.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | `dbt build` execution order per node: **unit tests → model materialization → data tests**. The docs say the model only materializes if its unit tests pass, which saves warehouse spend. Data tests run on the model after it's materialized. |
> | **B) ❌ Incorrect** | Unit tests specifically run before materialization — that is their defining characteristic. |
> | **C) ❌ Incorrect** | Unit tests do NOT run after materialization. Their entire purpose is to validate model logic before the model is written to the warehouse. |
> | **D) ❌ Incorrect** | Unit tests respect the DAG order; they run for each node in dependency order, not all at once before the DAG starts. |
>
> > 💡 **Key rule**: `dbt build` per-node sequence: **unit test → materialize → data test**. Unit test failure = model never runs. Data test failure = downstream nodes are skipped (not errored).

---

### Q8. ⭐
> **Subdomain 10.8 — `dbt build` upstream test failure behavior**

A `dbt build` run executes `model_a` successfully, then `model_a`'s data tests fail. `model_b` depends on `model_a`. What is the outcome for `model_b`?

- A) `model_b` runs anyway — test failures in upstream models do not block downstream builds.
- B) `model_b` is skipped — test failures in upstream models cause downstream nodes to skip, not error.
- C) `model_b` errors — the test failure propagates as an error to all downstream nodes.
- D) `model_b` runs but its own tests are skipped as a precaution.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `dbt build` is specifically designed to halt downstream work when upstream tests fail. |
> | **B) ✅ Correct** | When an upstream data test fails in `dbt build`, all downstream nodes are **skipped** (status = `skipped`). This is intentional: if the upstream data cannot be trusted, there is no point materializing dependent models. The job completes with a non-zero exit code due to the test failure, and `dbt retry` can re-run from the failure point. |
> | **C) ❌ Incorrect** | Downstream nodes receive `skipped` status, not `error`. The error is on the upstream test itself. |
> | **D) ❌ Incorrect** | dbt does not selectively skip tests on downstream nodes — the entire downstream node is skipped. |
>
> > 💡 **Key rule**: In `dbt build`, upstream test failure = downstream nodes **skip** (not error). Exit code is non-zero. Use `dbt retry` to resume from the failed test.

---

### Q9. ⭐
> **Subdomain 10.9 — `dbt retry` and infrastructure failures**

A dbt Cloud job fails due to a warehouse connectivity error before any nodes begin executing. The run results file shows zero nodes attempted. A developer runs `dbt retry`. What happens?

- A) `dbt retry` re-runs all models in the project since no successful runs exist.
- B) `dbt retry` raises an error and requires `--full-refresh` to proceed.
- C) `dbt retry` falls back to running the full model selection defined in the job.
- D) `dbt retry` is a no-op — if no nodes executed before the failure, there are no failed nodes to retry.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `dbt retry` reads `run_results.json` to find failed/errored nodes — it does not infer a full run when results are empty. |
> | **B) ❌ Incorrect** | `dbt retry` does not raise errors or require `--full-refresh` in this scenario. |
> | **C) ❌ Incorrect** | `dbt retry` does not fall back to the job's original model selection. It is strictly `run_results.json`-driven. |
> | **D) ✅ Correct** | `dbt retry` reads the `run_results.json` from the previous run and retries only nodes that `errored` or `failed`. If the failure was an infrastructure error before any nodes started (empty results), there is nothing to retry — `dbt retry` is effectively a **no-op**. The developer must re-run the job manually or fix the infrastructure issue first. |
>
> > 💡 **Key rule**: `dbt retry` = replay only `errored`/`failed` nodes from `run_results.json`. Infrastructure failure with zero executed nodes = **no-op retry**. Must re-run the job from scratch.

---

### Q10. ⭐
> **Subdomain 10.10 — `dbt clone` zero-copy behavior by platform**

A team runs `dbt clone` to create a developer-scoped copy of production models for a hotfix branch. Their warehouse is Postgres. What does `dbt clone` create for each cloned model?

- A) A schema-only empty table with no data.
- B) A full materialized copy of each table, duplicating all data.
- C) A view pointing to the production relation, acting as a lightweight proxy.
- D) A zero-copy clone using Postgres's native table clone syntax.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `dbt clone` creates a usable relation (view or clone), not an empty schema. |
> | **B) ❌ Incorrect** | `dbt clone` explicitly avoids full data copies — full table copies defeat the purpose of fast developer environment setup. |
> | **C) ✅ Correct** | The docs say that without zero-copy table cloning, dbt creates a simple **pointer view** (`select * from` the source object). It's a lightweight proxy, not a copy. |
> | **D) ❌ Incorrect** | Postgres does not support zero-copy cloning (metadata pointer swaps). That capability is limited to Snowflake, Databricks, and BigQuery. |
>
> > 💡 **Key rule**: `dbt clone` zero-copy support: **Snowflake** (CLONE), **Databricks** (shallow clone), **BigQuery** (table clone). **Postgres/Redshift** = pointer views. All behavior is automatic based on the adapter.

---

### Q11.
> **Subdomain 10.11 — `dbt retry` after a successful run**

A developer runs `dbt retry` right after a run where every node succeeded. What happens?

- A) It finishes as "no operation". There's nothing to retry.
- B) It re-runs every node in the project.
- C) It errors and asks for `--full-refresh`.
- D) It re-runs the last invocation's selection from the start.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say that if the previous run succeeded, retry finishes as no operation. |
> | **B) ❌ Incorrect** | Retry resumes from the point of failure. It doesn't re-run everything. |
> | **C) ❌ Incorrect** | No such requirement. |
> | **D) ❌ Incorrect** | It only re-executes from the failure point, using `run_results.json`. |
>
> > 💡 **Key rule**: `dbt retry` resumes from the failure via `run_results.json`. Previous run succeeded → no operation. Nothing ran before the failure → nothing to retry.

---

### Q12. ⭐
> **Subdomain 10.12 — `dbt ls` vs `dbt compile` warehouse connection requirement**

A developer in a CI pipeline wants to quickly list all modified models without running anything or touching the warehouse. Which command should they use?

- A) `dbt parse --select state:modified`
- B) `dbt run --select state:modified --dry-run`
- C) `dbt compile --select state:modified`
- D) `dbt ls --select state:modified --state ./prod-manifest`

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `dbt parse` validates the project without a warehouse connection, but it doesn't list selected nodes. |
> | **B) ❌ Incorrect** | `dbt run --dry-run` is not a valid dbt flag. |
> | **C) ❌ Incorrect** | `dbt compile` needs a data platform connection (it can run introspective queries) and writes compiled SQL. |
> | **D) ✅ Correct** | `dbt ls` reads your connection profile but doesn't connect to the database or run queries (dbt v2.0+). It lists the selected nodes. It is the correct tool for lightweight CI checks — listing nodes, validating selectors, or auditing the graph without touching the warehouse. |
>
> > 💡 **Key rule**: `dbt ls` = no database connection (dbt v2.0+). `dbt compile` = connection required. Use `dbt ls` for CI checks, selector validation, and graph audits.

---

### Q13. ⭐
> **Subdomain 10.13 — `dbt parse` and partial parsing in CI**

After a large merge to the main branch that restructures several macros, a CI job's `dbt run` begins picking up stale compiled artifacts from prior runs. What is the most targeted fix?

- A) Set `PARTIAL_PARSE: false` in the `dbt_project.yml`.
- B) Run `dbt clean` before `dbt run` to clear the compiled artifacts.
- C) Add `--no-partial-parse` to the `dbt run` command to force a full re-parse.
- D) Delete the entire `target/` directory before every CI run.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs say `PARTIAL_PARSE` is a global config set in `profiles.yml`, an environment variable or a CLI flag, not in `dbt_project.yml`. |
> | **B) ❌ Incorrect** | `dbt clean` also removes the partial-parse cache, but it deletes more than needed. |
> | **C) ✅ Correct** | `--no-partial-parse` tells dbt to **ignore the cached partial parse file** and re-parse the entire project from scratch. This is the recommended approach after macro restructuring or large merges where partial parse caching may be stale. It can be added to a dbt command: `dbt run --no-partial-parse`. dbt v2 job runs no longer support this flag. |
> | **D) ❌ Incorrect** | Deleting the full `target/` directory is overly aggressive — it removes all artifacts including run results and compiled SQL that may be needed for other CI steps. |
>
> > 💡 **Key rule**: Use `--no-partial-parse` (or `dbt parse --no-partial-parse` as a separate step) in CI after large merges to ensure a clean parse without stale cache artifacts.

---

### Q14. ⭐
> **Subdomain 10.14 — Ephemeral models and deferral**

A developer uses `--defer` on a feature branch. One of the referenced models, `int_orders_ephemeral`, is configured as `materialized: ephemeral`. The production manifest includes this model. What happens when the ephemeral model is referenced?

- A) The ephemeral model is skipped and dbt builds a view proxy pointing to production instead.
- B) Ephemeral models are never deferred — dbt always re-computes their CTE inline from source during the current run.
- C) The command errors because ephemeral models cannot be used with `--defer`.
- D) The ephemeral model is deferred to the production version, substituting the production CTE.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | No proxy is created for ephemeral models — they are always inline CTEs. |
> | **B) ✅ Correct** | Ephemeral models are compiled as **CTEs inlined into the models that reference them**. They have no persistent warehouse object. Therefore, `--defer` has no effect on them — dbt always recomputes the ephemeral CTE from its source SQL, regardless of what exists in the production manifest. |
> | **C) ❌ Incorrect** | Using `--defer` with ephemeral models does not cause an error; the flag is simply ignored for ephemeral nodes. |
> | **D) ❌ Incorrect** | Ephemeral models do not exist as warehouse objects — there is no production "version" to defer to. |
>
> > 💡 **Key rule**: Ephemeral models are **never deferred** because they have no warehouse object. `--defer` only applies to models that produce persistent relations (tables, views, incremental models).

---

### Q15. ⭐
> **Subdomain 10.15 — `state:modified` seed tracking limitation**

A team tracks state changes on seeds to avoid re-uploading large reference tables every CI run. One of their seeds is 1.5 MB. After changing several rows deep in the CSV, `state:modified` does not flag the seed as changed. Why?

- A) Seeds are never tracked by `state:modified` — you must always use `--full-refresh` for seeds.
- B) Seeds larger than 1 MB are tracked only by **file path**, not by content hash. Moving or renaming the file would trigger a change, but editing its rows would not.
- C) `state:modified` compares seeds using row count only; adding rows is detected but modifying existing rows is not.
- D) The seed tracking threshold is 10 MB; 1.5 MB seeds are tracked normally by content hash.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Seeds under 1 MB are tracked by content hash — only large seeds have this limitation. |
> | **B) ✅ Correct** | dbt tracks seed changes using a content hash (checksum of the CSV), but **only for seeds under 1 MB**. Seeds larger than 1 MB are tracked by **file path only**. This means content edits — adding, removing, or changing rows — are invisible to `state:modified` for large seeds. Only renaming or moving the file (path change) would register as a change. |
> | **C) ❌ Incorrect** | Row count is not used for seed tracking. The mechanism is content hash (for small seeds) or path (for large seeds). |
> | **D) ❌ Incorrect** | The threshold is 1 MB, not 10 MB. |
>
> > 💡 **Key rule**: Seeds **> 1 MB** are tracked by **path only** in state comparison. Content edits are invisible. For large seeds, consider splitting the file or forcing a re-upload with an explicit seed selector.

---

### Q16. ⭐
> **Subdomain 10.16 — Source freshness configuration**

A team wants freshness checks on a BigQuery source. What does dbt need to check it?

- A) `loaded_at_field`, always. Without it dbt can't compute freshness.
- B) A `unique_key` on the source.
- C) A `freshness` config with `warn_after` and/or `error_after`. `loaded_at_field` is optional.
- D) `freshness: enabled: true` in the project config.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `loaded_at_field` is optional. Without it, dbt uses warehouse metadata tables when possible. |
> | **B) ❌ Incorrect** | `unique_key` is for incremental models. |
> | **C) ✅ Correct** | If neither `warn_after` nor `error_after` is set, dbt doesn't check that resource. Each needs a `count` and a `period`. With `loaded_at_field` dbt runs a select. `loaded_at_query` (v1.10+) is an alternative, and setting both is a parse error. |
> | **D) ❌ Incorrect** | There's no such setting. `freshness: null` turns checks off for a table. |
>
> > 💡 **Key rule**: Freshness = a `freshness` config with `warn_after` / `error_after`. `loaded_at_field` is optional (warehouse metadata is used otherwise). Stale = nonzero exit code.

---

### Q17. ⭐
> **Subdomain 10.17 — `source_status:fresher+` selector**

A CI job should rebuild only the models downstream of sources that have received new data since the last freshness check. Which selector achieves this?

- A) `state:modified+ --select source:*`
- B) `source:* --select +state:modified`
- C) `result:fresher+`
- D) `source_status:fresher+`

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This syntax mixes selection methods incorrectly and does not leverage source freshness results. |
> | **B) ❌ Incorrect** | This is not valid selector syntax and conflates source selection with state comparison. |
> | **C) ❌ Incorrect** | `result:fresher` is not a valid selector. The correct method uses `source_status:fresher`, not `result:`. |
> | **D) ✅ Correct** | `source_status:fresher` selects sources that are **fresher than the last recorded state** (i.e., new data has arrived). The `+` suffix adds all downstream descendants. This selector requires a `--state` manifest from a prior `dbt source freshness` run (which produces `sources.json`). It enables data-arrival-driven pipelines: only rebuild when sources actually have new data. |
>
> > 💡 **Key rule**: `source_status:fresher+` = sources with new data since last check + all downstream models. Requires `--state` pointing to a manifest from a prior `dbt source freshness` run.

---

### Q18. ⭐
> **Subdomain 10.18 — `result:error` vs `result:fail` selectors**

After a failed `dbt build`, a developer wants to retry only the nodes that **errored** (e.g., models that failed to compile or run) while explicitly excluding tests that failed due to data quality issues. Which selector is correct?

- A) `result:error`
- B) `state:modified.body`
- C) `result:error result:fail`
- D) `result:fail`

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say `result:error` selects any resource that returned an error (models, tests, snapshots and so on). |
> | **B) ❌ Incorrect** | `state:modified.body` is a state comparison selector for detecting SQL body changes, not for retrying failed nodes. |
> | **C) ❌ Incorrect** | The space between these selectors = union (either errored OR failed). This would re-run both failing models and failing tests — not the desired behavior if you want to exclude data quality test failures. |
> | **D) ❌ Incorrect** | `result:fail` selects nodes with status `fail` — this is the status assigned to **tests** that fail (data quality assertion failures). It does not select errored models. |
>
> > 💡 **Key rule**: `result:error` = any resource that errored. `result:fail` = test nodes only. To re-run the models behind failed tests: `1+result:fail+`.

---

### Q19. ⭐
> **Subdomain 10.19 — `dbt compile --inline` for ad-hoc SQL**

A developer wants to compile a Jinja SQL snippet that uses `{{ ref('orders') }}` without creating a model file. Which command accomplishes this?

- A) `dbt compile --inline "SELECT * FROM {{ ref('orders') }}"`
- B) `dbt run --inline "SELECT * FROM {{ ref('orders') }}"`
- C) `dbt compile --ad-hoc "SELECT * FROM {{ ref('orders') }}"`
- D) `dbt parse --inline "SELECT * FROM {{ ref('orders') }}"`

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | `dbt compile --inline "<sql>"` compiles an ad-hoc Jinja SQL string without requiring a model file. It resolves `{{ ref() }}`, `{{ source() }}`, macros, and variables against the current project and target, then prints the compiled SQL. Useful for debugging Jinja expressions or quickly checking what a snippet compiles to. Note: requires a **warehouse connection** (like all `dbt compile` invocations). |
> | **B) ❌ Incorrect** | `dbt run` does not support `--inline`. It executes model files, not inline SQL. |
> | **C) ❌ Incorrect** | `--ad-hoc` is not a valid dbt flag. |
> | **D) ❌ Incorrect** | `dbt parse` does not support `--inline`. It parses project files, not inline SQL. |
>
> > 💡 **Key rule**: `dbt compile --inline "<jinja-sql>"` = ad-hoc compilation of a SQL snippet. No model file needed, but warehouse connection required. Great for Jinja debugging.

---

### Q20. ⭐
> **Subdomain 10.20 — `--favor-state` flag behavior**

A developer runs `dbt run --select orders+ --defer --state ./prod-manifest`. For nodes that exist in both the dev target (partially built from yesterday) and the production manifest, which relation does dbt use by default? **Select TWO correct answers.**

- A) By default (no `--favor-state`), dbt prefers the **production manifest** relation always.
- B) By default (no `--favor-state`), dbt prefers the **dev target** relation if it exists there.
- C) Adding `--favor-state` causes dbt to prefer the **state manifest** (production) relation over the dev target.
- D) Adding `--favor-state` causes dbt to prefer the **dev target** relation over the state manifest.

> [!success]- Answer & Explanations
> **✅ Correct: B, C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Without `--favor-state`, production is the fallback, not the preference. Dev target takes priority when a relation exists there. |
> | **B) ✅ Correct** | The **default `--defer` behavior** prefers the developer's own target schema. If a relation exists in the dev target (even if outdated), dbt uses it — deferring to production only for relations that do NOT exist in dev at all. |
> | **C) ✅ Correct** | `--favor-state` **flips the priority**: dbt now prefers the state manifest (production) relation over whatever is in the dev target. This ensures developers always work against production-fresh data even when stale dev relations exist. |
> | **D) ❌ Incorrect** | This describes the default behavior (no `--favor-state`), not what `--favor-state` adds. |
>
> > 💡 **Key rule**: Default `--defer` = dev target first → prod state as fallback. `--favor-state` = prod state first → dev target as fallback. Use `--favor-state` in CI or when dev relations may be stale.

---

### Q21. ⭐
> **Subdomain 10.21 — `source:` vs `source_status:` selector methods**

A platform team wants to build only the models downstream of sources whose raw data has actually arrived since the last run. They author a job with the step:

```bash
dbt build --select source:fresher+
```

The job runs successfully but builds **zero models**, even though new data has clearly landed in some sources. What is the issue, and what is the correct command? **Select TWO correct answers.**

- A) The job will work as written if the team upgrades to the Fusion engine, which auto-resolves `source:fresher+` as a freshness-state selector.
- B) The correct selector method for "sources with new data since the last freshness check" is `source_status:fresher+`, which compares the current `sources.json` against a prior one provided via `--state`.
- C) `source_status:` accepts multiple values such as `fresher`, `stale`, and `error` — the team should use `source_status:fresher,stale+` to capture all changes.
- D) `source:fresher+` is interpreted as a **name lookup** for a source literally named `fresher`. Unless one exists, the selector matches nothing and the run is a silent no-op.
- E) `source:fresher+` is the correct selector but requires the `--full-refresh` flag to register new freshness state.

> [!success]- Answer & Explanations
> **✅ Correct: B, D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The Fusion engine does not change selector method semantics. `source:` remains a name lookup regardless of engine. |
> | **B) ✅ Correct** | The correct selector is **`source_status:fresher+`** — a state-aware selector that compares the current `sources.json` (from a fresh `dbt source freshness` run) against a prior one supplied via `--state path/to/previous/`. Sources whose `max_loaded_at` is newer in the current run are tagged `fresher` and selected, along with their downstream models. The full correct command is: `dbt build --select source_status:fresher+ --state path/to/previous/`. Without `--state`, this also resolves to zero nodes. |
> | **C) ❌ Incorrect** | The docs document only the value `fresher` for `source_status:`. |
> | **D) ✅ Correct** | `source:` is the **name-based** selector method — it expects a source's declared name (e.g., `source:snowplow+`). `source:fresher+` is interpreted as "find a source literally **named** `fresher` plus its descendants." Since virtually no project defines a source by that name, the selector resolves to **zero nodes** and the run silently does nothing. This is one of the most common dbt selector traps. |
> | **E) ❌ Incorrect** | `--full-refresh` controls incremental rebuild behavior — it has no relationship to freshness state detection. The underlying selector method is still wrong. |
>
> > 💡 **Key rule**: `source:<name>+` = **name lookup** (no `--state` needed). `source_status:fresher+` = **state-aware freshness selector** (requires `--state` with prior `sources.json`; only `fresher` is documented). Mistyping `source_status` as `source` is a silent no-op, not an error.

---

*Topic 10 — dbt Commands & Node Selection | 21 questions | Architect-level*
