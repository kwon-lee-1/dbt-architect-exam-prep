# Topic 4c: Blue/Green Deployments and dbt clone — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 12 questions | Architect-level | ⭐ = High-Yield
> The official docs list blue/green only as a `dbt clone` use case. The swap steps are a community pattern.

---

### Q1. ⭐
> **Subdomain 4c.1 — What `dbt clone` does**

A team runs `dbt clone --state ./prod_artifacts` on a platform where a production model exists as a table. What does dbt create in the target schema?

- A) A zero-copy clone, if the platform supports it (Snowflake, Databricks, BigQuery). Otherwise a pointer view (`select * from` the source).
- B) Always a pointer view, on every platform.
- C) A full physical copy of the table, on every platform.
- D) Nothing, until `--defer` is passed.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say that if the platform supports zero-copy cloning of tables (Snowflake, Databricks, or BigQuery) and the model exists as a table in the source environment, dbt creates it as a clone. Otherwise it creates a simple pointer view. |
> | **B) ❌ Incorrect** | Pointer views are the fallback, not the default on clone-capable platforms. |
> | **C) ❌ Incorrect** | Zero-copy clones aren't full copies, and the fallback is a view. |
> | **D) ❌ Incorrect** | `dbt clone` relies on `--defer` but doesn't need it passed in the dbt platform CLI. |
>
> > 💡 **Key rule**: Clone = zero-copy on Snowflake, Databricks, BigQuery (when the model is a table). Otherwise a pointer view.

---

### Q2. ⭐
> **Subdomain 4c.2 — Pre-existing relations**

`dbt clone` skips several models that already exist in the target schema. How do you recreate them?

- A) Add `--defer`.
- B) Use `state:modified` in the selector.
- C) Add `--full-refresh`.
- D) Wait for the production job to finish.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `--defer` controls how unselected upstream nodes resolve, not whether existing relations are recreated. |
> | **B) ❌ Incorrect** | Selectors choose nodes. They don't change the skip behavior. |
> | **C) ✅ Correct** | By default `dbt clone` doesn't recreate pre-existing relations in the current target. `--full-refresh` recreates all of them. |
> | **D) ❌ Incorrect** | Job timing isn't the cause. |
>
> > 💡 **Key rule**: `dbt clone` skips existing relations by default. `--full-refresh` recreates them.

---

### Q3.
> **Subdomain 4c.3 — Deferral with `dbt clone`**

A developer runs `dbt clone` in the Studio IDE and the unselected upstream models aren't resolved against production. What should they check?

- A) That `--full-refresh` is set.
- B) That the "Defer to production" toggle is on. The dbt platform CLI includes `--defer` automatically.
- C) That the job runs on a schedule.
- D) That the project uses a staging environment.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `--full-refresh` only recreates existing relations. |
> | **B) ✅ Correct** | `dbt clone` relies on `--defer`. The platform CLI includes the flag automatically. In the Studio IDE you enable the "Defer to production" toggle first. |
> | **C) ❌ Incorrect** | Scheduling has nothing to do with it. |
> | **D) ❌ Incorrect** | Not required for deferral. |
>
> > 💡 **Key rule**: Platform CLI adds `--defer` automatically. Studio IDE needs the "Defer to production" toggle.

---

### Q4. ⭐
> **Subdomain 4c.4 — Clone vs deferral**

A BI team wants to test downstream dashboards against production-like data before a release. A separate team only needs to test dbt logic in CI and wants the cheapest option. Which choices fit?

- A) Deferral for both.
- B) Clone for both.
- C) Deferral for the BI test, clone for CI.
- D) Clone for the BI test, deferral for CI.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Deferral only changes how dbt resolves `ref()`. A BI tool needs real objects in the warehouse. |
> | **B) ❌ Incorrect** | Clone needs compute and creates additional objects. The docs say deferral is often a cheaper and simpler alternative. |
> | **C) ❌ Incorrect** | Reversed. |
> | **D) ✅ Correct** | The docs list "testing code changes on downstream dependencies in your BI tool" as a clone use case, and note that deferral is in many cases cheaper and simpler. |
>
> > 💡 **Key rule**: Clone creates real warehouse objects (needs compute). Deferral is often cheaper and simpler.

---

### Q5.
> **Subdomain 4c.5 — Documented clone use cases**

Which of these is a documented use case for `dbt clone`?

- A) Replacing `dbt test` in deployment jobs.
- B) Handling incremental models in dbt CI jobs, on warehouses with zero-copy cloning.
- C) Running snapshots in parallel.
- D) Automatically reducing warehouse costs.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Clone doesn't run tests. |
> | **B) ✅ Correct** | The docs list four uses: blue/green continuous deployment, cloning production into development schemas, handling incremental models in CI jobs, and testing downstream changes in your BI tool. |
> | **C) ❌ Incorrect** | Not a documented use. |
> | **D) ❌ Incorrect** | Clone actually needs compute and creates extra objects. |
>
> > 💡 **Key rule**: Clone uses: blue/green, prod → dev schemas, incrementals in CI, BI testing.

---

### Q6.
> **Subdomain 4c.6 — Incremental models in CI**

In a Slim CI job, a modified incremental model builds in full because it doesn't exist in the PR schema yet. What do the docs suggest?

- A) Run the job with `--full-refresh` always.
- B) Clone production's incremental tables into the PR schema first, then build: `dbt clone --select state:modified+,config.materialized:incremental,state:old`.
- C) Switch the model to a view in CI.
- D) Disable `is_incremental()`.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | That is the problem: it builds in full. |
> | **B) ✅ Correct** | With the clone in place, the incremental model runs in incremental mode. `state:old` excludes brand-new incremental models that don't exist in production. It needs dbt 1.6+ and a warehouse with zero-copy cloning, otherwise you only get pointer views. |
> | **C) ❌ Incorrect** | Not suggested. |
> | **D) ❌ Incorrect** | Not suggested. |
>
> > 💡 **Key rule**: Clone existing incrementals into the PR schema before `dbt build --select state:modified+`.

---

### Q7. ⭐
> **Subdomain 4c.7 — Is blue/green built in?**

A teammate says "run the built-in blue/green command". What's the accurate answer?

- A) `dbt blue-green` exists in dbt v1.6+.
- B) Blue/green is a setting on the Production environment.
- C) The docs list blue/green as a use case for `dbt clone`. The database swap is a custom macro you run with `dbt run-operation`.
- D) It's an Enterprise+ job type.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | No such command. |
> | **B) ❌ Incorrect** | No such environment setting. |
> | **C) ✅ Correct** | The docs mention "blue/green continuous deployment" only as a `dbt clone` use case on zero-copy warehouses. The swap (for example Snowflake `alter database prod swap with stage`) is a macro you write and run via `dbt run-operation`. |
> | **D) ❌ Incorrect** | Not a job type or plan feature. |
>
> > 💡 **Key rule**: `swap_database` is a custom macro, not a built-in command.

---

### Q8. ⭐
> **Subdomain 4c.8 — Job step order**

Which job command order matches the community blue/green pattern?

- A) `dbt run-operation swap_database` → `dbt run` → `dbt test`
- B) `dbt test` → `dbt run` → `dbt run-operation swap_database`
- C) `dbt run` → `dbt test` → `dbt run-operation swap_database`
- D) `dbt run` → `dbt run-operation swap_database` → `dbt test`

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Swapping first promotes an unbuilt database. |
> | **B) ❌ Incorrect** | Testing before building tests old data. |
> | **C) ✅ Correct** | Build in the stage database, test it, then swap so the tested data becomes prod. |
> | **D) ❌ Incorrect** | Swapping before testing puts untested data in prod. |
>
> > 💡 **Key rule**: `dbt run` → `dbt test` → `dbt run-operation swap_database`.

---

### Q9.
> **Subdomain 4c.9 — Test failure**

In the same job, `dbt test` fails. What happens to the swap step?

- A) It runs anyway.
- B) It runs only for models whose tests passed.
- C) It doesn't run. A failed step stops the job, so production is unchanged.
- D) It runs but is flagged degraded.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | A failed command stops the remaining steps. |
> | **B) ❌ Incorrect** | The swap moves a whole database, not individual models. |
> | **C) ✅ Correct** | The swap is the last step, so it never runs after a failure. Production stays as it was. |
> | **D) ❌ Incorrect** | There's no degraded swap. |
>
> > 💡 **Key rule**: Failed run or test stops the job, so no swap.

---

### Q10.
> **Subdomain 4c.10 — Partial runs**

An engineer runs `dbt run --select state:modified` in the stage database and then triggers the swap. What is the risk?

- A) None. dbt tracks what was rebuilt.
- B) The swap fails automatically.
- C) Only modified models are swapped.
- D) The swap moves the whole stage database. Anything not rebuilt may be stale or missing, so production gets an inconsistent state.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt doesn't check this. The swap is a custom macro. |
> | **B) ❌ Incorrect** | It just swaps the databases. |
> | **C) ❌ Incorrect** | A database swap isn't per model. |
> | **D) ✅ Correct** | This follows from how a database swap works. Only swap after a full build. |
>
> > 💡 **Key rule**: The swap moves the whole database. Swap only after a full build.

---

### Q11. ⭐
> **Subdomain 4c.11 — Views after the swap**

After a swap, views in the warehouse return stale data or fail with "does not exist" errors. What is the community fix?

- A) Re-run `dbt test`.
- B) Use `--full-refresh` on every model.
- C) Override `ref` (and `source`) so compiled SQL doesn't include the database name.
- D) Swap schemas instead of databases.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Tests don't change view definitions. |
> | **B) ❌ Incorrect** | Rebuilding doesn't fix fully qualified names baked into views. |
> | **C) ✅ Correct** | Fully qualified references in views point to a database name that now holds different data. Dropping the database name from `ref` and `source` fixes it. |
> | **D) ❌ Incorrect** | The thread advises against schema swapping because it can break views and custom schemas. |
>
> > 💡 **Key rule**: Override `ref` / `source` to drop the database name so views follow the swap.

---

### Q12.
> **Subdomain 4c.12 — Platforms**

A team wants blue/green on BigQuery. What does the community thread say?

- A) Use `alter database ... swap with`.
- B) Datasets can't be renamed, so the thread links a workaround.
- C) BigQuery doesn't support `dbt clone`.
- D) Use `dbt clone` only, no swap needed.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | That's Snowflake. |
> | **B) ✅ Correct** | The Snowflake `swap with` doesn't exist for BigQuery datasets, so the thread links a workaround. |
> | **C) ❌ Incorrect** | BigQuery is one of the zero-copy clone platforms. |
> | **D) ❌ Incorrect** | Clone doesn't swap anything. |
>
> > 💡 **Key rule**: Snowflake swaps databases. BigQuery datasets can't be renamed. Clone is zero-copy on Snowflake, Databricks, BigQuery.

---

*[End of Topic 4c — 12 questions]*
