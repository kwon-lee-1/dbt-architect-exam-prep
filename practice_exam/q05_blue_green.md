# Topic 4c: Blue/Green Deployments — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 20 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 4c.1 — Views breaking after swap**

After a successful blue/green deployment and database swap on Snowflake, downstream BI tools begin returning stale data even though the swap completed without errors. What is the most likely cause?

- A) The swap operation didn't complete atomically — some tables were swapped while others were not.
- B) Views in downstream BI tools were compiled with hardcoded database names. After the swap, the hardcoded name refers to the old (demoted) blue database.
- C) Snowflake's `SWAP WITH` command has a replication lag of several minutes before BI tools see updated data.
- D) The blue/green swap only works for tables — views must be manually recreated after each swap.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Snowflake's `SWAP WITH` is atomic — it swaps metadata pointers in a single operation. Partial swaps don't occur. |
> | **B) ✅ Correct** | When dbt compiles views, it includes the fully-qualified database name by default. After the swap, the database that was blue becomes green and vice versa — views with hardcoded names now point to the **demoted** (old blue) database, returning stale data. **Fix**: override `ref()` and `source()` macros to exclude the database qualifier using `builtins.ref(model).include(database=false)`. |
> | **C) ❌ Incorrect** | Snowflake's atomic swap is instantaneous — there is no documented replication lag. |
> | **D) ❌ Incorrect** | Views are affected by the swap (they reference the old database name), but they don't need manual recreation — the fix is in the macro override, not manual recreation. |
>
> > 💡 **Key rule**: Override `ref()` and `source()` to exclude database qualifier: `builtins.ref(model).include(database=false)`.

---

### Q2. ⭐
> **Subdomain 4c.2 — Snapshots and blue/green**

After several blue/green deployments, the team notices gaps in snapshot history — `dbt_valid_to` records show unexpected null values and overlapping periods. What caused this?

- A) Snapshot tables were included in the database swap — `dbt_valid_to` continuity tracking breaks when the snapshot table's physical database changes.
- B) The blue/green swap runs `dbt snapshot` on the wrong environment during the swap phase.
- C) Snapshots require `--full-refresh` after every blue/green swap to rebuild the history.
- D) The swap operation drops and recreates snapshot tables, losing all historical records.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Snapshots maintain `dbt_valid_from` and `dbt_valid_to` continuity by tracking changes to a single physical table location. When a blue/green swap moves the snapshot table to a different database, the SCD tracking mechanism is disrupted — subsequent snapshot runs don't recognize the continuity, causing gaps and overlaps. **Fix**: store snapshots in a **dedicated, non-swapped database** with a custom `ref_snapshot()` macro that always routes to that fixed location. |
> | **B) ❌ Incorrect** | The swap operation doesn't run `dbt snapshot` — it's a metadata pointer swap. |
> | **C) ❌ Incorrect** | `--full-refresh` on snapshots destroys all history — that's worse than the problem. |
> | **D) ❌ Incorrect** | `SWAP WITH` swaps metadata pointers — it doesn't drop tables. |
>
> > 💡 **Key rule**: Snapshots must live in a **dedicated non-swapped database**. Include them in the swap = broken `dbt_valid_to` continuity.

---

### Q3.
> **Subdomain 4c.3 — Incremental models after swap**

An incremental model is part of a blue/green deployment pipeline. After a swap, the next deployment run shows the incremental model is missing rows that were processed in the previous deployment. Why?

- A) Incremental models always require `--full-refresh` in blue/green deployments — they can't be used incrementally.
- B) After the swap, the demoted blue database becomes the new staging baseline. The incremental model's next run adds only rows newer than the stale demoted state, potentially missing rows from the last production window.
- C) The swap operation resets the incremental model's high-water mark to the initial load date.
- D) Incremental models are incompatible with the atomic swap mechanism on all platforms.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Incremental models can be used in blue/green, but require special handling — they don't always need `--full-refresh`. |
> | **B) ✅ Correct** | After a swap, the old blue becomes the new green (staging). The incremental table it contains represents the state from the **deployment before last**. The next green deployment runs incrementally on top of this stale baseline — rows processed in the most recent (now-production) blue run may not exist in the new green baseline, causing apparent missing data. **Fix**: run `dbt run --full-refresh --select <incremental_models>` after each swap, or maintain a high-water mark in a non-swapped table. |
> | **C) ❌ Incorrect** | The swap doesn't reset high-water marks — it just changes which table is in which database. |
> | **D) ❌ Incorrect** | Incremental models are not incompatible — they just require careful handling post-swap. |
>
> > 💡 **Key rule**: Post-swap: incremental models have stale baseline. Run `--full-refresh` on incrementals after each swap.

---

### Q4.
> **Subdomain 4c.4 — Platform support for blue/green**

A data team using Amazon Redshift proposes implementing blue/green deployments to achieve zero-downtime releases. What is the fundamental problem with this approach?

- A) Redshift's `CLONE` command is too slow for production-scale blue/green deployments.
- B) Redshift does not support database/schema renaming or atomic swap operations — blue/green is not viable without downtime.
- C) Blue/green deployments on Redshift require the Advanced CI plan feature.
- D) Redshift's blue/green support is in beta and not yet recommended for production use.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Redshift doesn't have a `CLONE` command equivalent for zero-copy table cloning — the issue isn't speed, it's the absence of the feature. |
> | **B) ✅ Correct** | **Redshift does not support database/schema renaming or atomic swap operations**. Blue/green deployments require an atomic swap (like Snowflake's `SWAP WITH`) to achieve zero downtime. Without this capability, any "swap" on Redshift involves sequential DDL operations that create a downtime window. Blue/green is **not viable on Redshift**. |
> | **C) ❌ Incorrect** | Blue/green is an architectural deployment pattern — it's not a dbt Cloud plan feature. |
> | **D) ❌ Incorrect** | This is not a beta limitation — Redshift simply lacks the required database primitives. |
>
> > 💡 **Key rule**: Redshift = **no atomic swap** = blue/green not viable. Snowflake ✅, Databricks ✅, BigQuery ✅ (with workarounds).

---

### Q5. ⭐
> **Subdomain 4c.5 — dbt clone vs deferral**

Before a blue/green cutover, a BI team wants to validate dashboards against the staging (green) data before the swap executes. Should they use `dbt clone` or deferral for this validation?

- A) Deferral — it's faster and cheaper since no data is physically copied.
- B) `dbt clone` — it creates real relations in the staging schema that BI tools can query, whereas deferral is invisible to external tools.
- C) Either approach works — deferral and clone are interchangeable for BI validation.
- D) Neither — BI validation must be done after the swap, not before.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Deferral resolves `ref()` calls within dbt — it does not create physical tables visible to external BI tools. BI tools querying the warehouse won't benefit from deferral. |
> | **B) ✅ Correct** | `dbt clone` creates **real relations** (zero-copy clones on Snowflake, pointer views on other platforms) in the staging schema. BI tools can connect to these real tables/views and validate dashboards against green data before the swap executes. Deferral is a dbt-internal mechanism — external tools are unaware of it. |
> | **C) ❌ Incorrect** | They serve fundamentally different purposes — clone creates physical objects visible to external tools; deferral is internal to dbt's DAG resolution. |
> | **D) ❌ Incorrect** | Pre-swap BI validation is precisely the use case for `dbt clone` — it enables pre-cutover validation without committing to the swap. |
>
> > 💡 **Key rule**: Use `dbt clone` when BI/apps need realistic data before cutover. Use deferral for dbt-internal CI cost optimization.

---

### Q6.
> **Subdomain 4c.6 — Partial run swap risk**

A team uses blue/green deployments. An on-call engineer triggers the `swap_database` operation after running only a subset of models (`dbt run --select state:modified`). What is the risk?

- A) The swap will fail because `swap_database` requires a full run artifact to verify completion.
- B) The green (staging) database will be incomplete — some models reflect new code while others are from the previous deployment. Swapping makes this incomplete state production.
- C) Only the modified models will swap — unmodified models stay in the blue database automatically.
- D) The swap is safe because dbt tracks which models were built in this run vs the previous run.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `dbt run-operation swap_database` is a custom macro — it doesn't validate run completeness before executing. |
> | **B) ✅ Correct** | `swap_database` swaps the **entire database** — not individual models. If only a subset of models was built in green, the swap promotes an incomplete state to production. Some models will have new code, others stale code from the previous deployment cycle. Blue/green swaps must only be executed after a **complete full run** of all models against green. |
> | **C) ❌ Incorrect** | The swap is at the database level — it does not selectively swap individual models. |
> | **D) ❌ Incorrect** | dbt does not validate run completeness before allowing a swap operation. |
>
> > 💡 **Key rule**: **Never swap after a partial `--select` run.** Green must be fully built before `swap_database` is safe.

---

### Q7.
> **Subdomain 4c.7 — Failure safety**

A blue/green deployment job runs `dbt run` followed by `dbt test` in the green environment. Three data quality tests fail. What happens to the production (blue) environment?

- A) Production is automatically rolled back to the previous deployment.
- B) Production remains unchanged — the swap never executes because tests failed, so blue stays live.
- C) Production is partially affected — the models that passed testing are swapped.
- D) Production is swapped but flagged as degraded in the dbt Catalog health signals.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is nothing to roll back — production was never touched. Blue/green's design is that blue is untouched until the explicit swap command runs. |
> | **B) ✅ Correct** | If `dbt test` fails in green, the job aborts before `dbt run-operation swap_database` executes. **Blue (production) remains live and completely unchanged**. This is the core safety guarantee of blue/green deployments — failures are safe by design. Only after a full successful run AND all tests passing does the swap execute. |
> | **C) ❌ Incorrect** | The swap is all-or-nothing — there is no partial swap of "passing" models. |
> | **D) ❌ Incorrect** | The swap does not execute — nothing about production changes. |
>
> > 💡 **Key rule**: Blue/green failure = **safe**. Test failure aborts before swap. Blue stays live. No partial swaps.

---

### Q8.
> **Subdomain 4c.8 — dbt clone behavior**

A team uses `dbt clone` to populate the staging (green) environment before a blue/green deployment. They run `dbt clone --state ./prod_artifacts` but notice that several models already present in the staging schema are not recreated. What is the default behavior and how can they force recreation?

- A) `dbt clone` always recreates all models — if some are skipped, the state artifacts are stale.
- B) By default, `dbt clone` **skips pre-existing relations** in the target schema. Use `--full-refresh` to force recreation of existing clones.
- C) `dbt clone` only creates new models (`state:new`) — use `state:modified` to include modified clones.
- D) Pre-existing relations are skipped because they are locked by the production job. Wait for the production job to complete before running `dbt clone`.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The default behavior is to skip pre-existing relations — not recreate all. This is intentional to avoid unnecessary work. |
> | **B) ✅ Correct** | By default, `dbt clone` **skips pre-existing relations** in the target schema. To force all clones to be recreated (useful when you want the staging environment to be a fresh copy of production), add the `--full-refresh` flag: `dbt clone --state ./prod_artifacts --full-refresh`. |
> | **C) ❌ Incorrect** | `dbt clone` is not driven by `state:new` or `state:modified` — it clones selected models from the source state to the target schema. |
> | **D) ❌ Incorrect** | Locking is not the cause — `dbt clone` uses zero-copy cloning which doesn't require the source table to be idle. |
>
> > 💡 **Key rule**: `dbt clone` default = **skips pre-existing relations**. Add `--full-refresh` to recreate them.

---

---

### Q9.
> **Subdomain 4c.9 — Blue/green core problem**

What core deployment problem does the blue/green strategy solve that standard dbt deployments cannot?

- A) It eliminates the need for test runs since both environments are always validated.
- B) It prevents mid-run data inconsistency — in a standard deployment, a job failure leaves live queries hitting partially-built tables. Blue/green builds everything in staging first and only swaps to production after all tests pass.
- C) It reduces warehouse compute costs by running models only on changed data.
- D) It enables cross-warehouse deployments by maintaining two separate warehouse connections simultaneously.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Blue/green still requires test runs — in fact, tests must pass in the green environment before the swap is allowed. It does not eliminate tests. |
> | **B) ✅ Correct** | In a **standard deployment**, if a dbt job fails mid-run, live queries are hitting a mix of old and new (partially-built) tables — data inconsistency is immediate. **Blue/green** solves this by building all models in the green (staging) environment while blue (production) remains fully live and untouched. Only after all models build and all tests pass does an **atomic swap** occur. Live queries never hit a partial state. |
> | **C) ❌ Incorrect** | Blue/green deploys the full model set in green — it does not optimize for incremental computation. Cost reduction is not the primary motivation. |
> | **D) ❌ Incorrect** | Blue/green operates within a single warehouse (e.g., two databases in Snowflake). It does not involve cross-warehouse deployments. |
>
> > 💡 **Key rule**: Blue/green solves mid-run inconsistency: standard deployment = partial tables live during run. Blue/green = atomic swap, production never partially updated.

---

### Q10.
> **Subdomain 4c.10 — Databricks blue/green viability**

A team using Databricks as their data warehouse wants to implement blue/green deployments. A colleague claims Databricks doesn't support it. Is this correct?

- A) Correct — Databricks does not support zero-copy cloning or atomic swaps.
- B) Incorrect — Databricks supports blue/green using **shallow clone** for zero-copy cloning and a schema swap for the atomic cutover. It is fully viable.
- C) Partially correct — Databricks supports zero-copy cloning but requires brief downtime during the swap step.
- D) Incorrect — Databricks supports blue/green but only when using Delta Live Tables, not standard dbt models.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Databricks does support both zero-copy cloning and atomic schema swaps. |
> | **B) ✅ Correct** | Databricks is fully viable for blue/green deployments. It supports **shallow clone** (zero-copy cloning of Delta tables) and **schema swap** for the atomic cutover. This makes it one of the preferred platforms for blue/green alongside Snowflake. The non-viable platforms are Redshift and Postgres, which lack rename/swap support. |
> | **C) ❌ Incorrect** | The schema swap on Databricks is atomic — there is no documented brief downtime window. |
> | **D) ❌ Incorrect** | Blue/green on Databricks works with standard dbt models and does not require Delta Live Tables. |
>
> > 💡 **Key rule**: Databricks = viable for blue/green (shallow clone + schema swap). Non-viable: Redshift (no rename/swap), Postgres (sequential DDL only).

---

### Q11.
> **Subdomain 4c.11 — BigQuery blue/green viability**

A team using BigQuery wants to implement a blue/green deployment. Which of the following accurately describes BigQuery's blue/green support?

- A) BigQuery is not viable for blue/green — it has no support for dataset cloning or swapping.
- B) BigQuery supports blue/green using native table cloning and a dataset-level swap workaround. It is viable but requires more configuration than Snowflake.
- C) BigQuery is fully equivalent to Snowflake for blue/green — it uses identical `CLONE` and `SWAP WITH` syntax.
- D) BigQuery supports blue/green only in Enterprise+ accounts where dataset-level permissions can be swapped atomically.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | BigQuery does support table cloning and has a dataset swap workaround — it is viable. |
> | **B) ✅ Correct** | BigQuery supports **table clone** (zero-copy) and uses a **dataset swap workaround** (not a native `SWAP` command like Snowflake's `SWAP WITH`). This makes it viable for blue/green but with more complexity. It is in the "supported with workarounds" category — unlike Snowflake and Databricks, which have more native support. |
> | **C) ❌ Incorrect** | BigQuery uses table clone syntax, not Snowflake's `CLONE` or `SWAP WITH` commands. The approach is similar in outcome but different in syntax and atomicity guarantees. |
> | **D) ❌ Incorrect** | BigQuery blue/green is not gated on dbt Cloud Enterprise+ — it is a warehouse-side capability, not a dbt plan feature. |
>
> > 💡 **Key rule**: BigQuery = viable for blue/green with dataset swap workaround (not native `SWAP WITH`). Snowflake and Databricks have more native support.

---

### Q12.
> **Subdomain 4c.12 — swap_database operation**

After all models build and tests pass in the green environment, an engineer runs `dbt run-operation swap_database`. What does this operation do?

- A) It copies all data from green to blue, making green's data available in the production blue schema.
- B) It executes a custom macro that performs an **atomic database swap** — green becomes production and blue becomes the new staging. No data is copied; only metadata pointers change.
- C) It deletes the blue database and renames green to blue.
- D) It runs a final test suite in both environments before permitting the swap.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | No data is copied — that would be slow and expensive. The swap changes metadata pointers, not data. |
> | **B) ✅ Correct** | `dbt run-operation swap_database` executes a **custom macro** (e.g., using Snowflake's `ALTER DATABASE ... SWAP WITH`) that performs an **atomic metadata pointer swap**. Green becomes the live production database; blue becomes the new staging for the next deployment. Because it's a metadata operation (not a data copy), it is near-instantaneous — this is the "zero downtime" mechanism. |
> | **C) ❌ Incorrect** | Blue is not deleted — it becomes the new staging, which is immediately available as a rollback point. |
> | **D) ❌ Incorrect** | Tests must already have passed before `swap_database` is called — it does not trigger additional tests. |
>
> > 💡 **Key rule**: `swap_database` = atomic metadata pointer swap (no data copy). Green → production. Blue → new staging (rollback point).

---

### Q13.
> **Subdomain 4c.13 — Blue/green rollback**

A blue/green deployment swap completes successfully. Ten minutes later, the data team discovers a critical data quality issue in the newly promoted green environment (now production). What is the rollback procedure?

- A) Restore from a warehouse snapshot that was taken before the swap.
- B) Re-run the full dbt deployment job against the old blue database to rebuild it.
- C) Execute `swap_database` again — the old blue database (now staging) is still intact and becomes production instantly.
- D) Manually copy tables from the staging database back to production.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Warehouse snapshots are slower and more complex than the blue/green rollback mechanism. They're a last resort, not the designed rollback path. |
> | **B) ❌ Incorrect** | Rebuilding the old blue database is unnecessary — it was not destroyed during the swap. It exists intact as the current staging database. |
> | **C) ✅ Correct** | One of blue/green's key benefits is **instant rollback**: after a swap, the **old blue database is preserved as the new staging** and contains the last known-good production state. Running `swap_database` again swaps them back — the old blue (now staging) becomes production again. This is near-instantaneous and requires no data rebuild. |
> | **D) ❌ Incorrect** | Manual table copying is slow, error-prone, and unnecessary given the atomic swap mechanism. |
>
> > 💡 **Key rule**: Blue/green rollback = run `swap_database` again. Old blue is preserved as staging — swap back is instant.

---

### Q14.
> **Subdomain 4c.14 — Storage implications**

A CTO asks why the data team's Snowflake storage costs doubled after adopting blue/green deployments. What is the explanation?

- A) dbt clone creates full physical copies of every table, doubling storage permanently.
- B) Blue/green requires maintaining both the blue (production) and green (staging) databases simultaneously, which doubles storage requirements compared to a single-database setup.
- C) The swap operation leaves orphaned temporary tables in both databases that accumulate over time.
- D) dbt now runs two job runs per deployment cycle instead of one, creating twice as many warehouse query logs.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | On Snowflake, `dbt clone` uses **zero-copy cloning** — it creates metadata pointers, not physical copies. Storage is only consumed when data diverges from the original. |
> | **B) ✅ Correct** | Blue/green deployments require maintaining **two complete databases** at all times — the current production (blue) and the staging being built (green). This inherently requires approximately **2× the storage** of a standard single-database setup. This is a known trade-off: the cost of zero-downtime deployment is double the storage. Teams should factor this into their warehouse cost planning. |
> | **C) ❌ Incorrect** | The swap operation is a metadata operation and does not leave orphaned tables. |
> | **D) ❌ Incorrect** | Query logs do not meaningfully contribute to storage costs compared to the data tables themselves. |
>
> > 💡 **Key rule**: Blue/green = **2× storage** required (blue + green databases both exist simultaneously). This is a known trade-off for zero-downtime deployments.

---

### Q15.
> **Subdomain 4c.15 — Zero-copy clone platforms**

A team wants to use `dbt clone` to populate their green (staging) environment with production data before a blue/green deployment. They are concerned about warehouse compute cost during this step. On which platforms does `dbt clone` perform a **zero-copy clone** (no data scanning or movement)?

- A) All platforms supported by dbt Cloud — zero-copy cloning is a dbt feature, not platform-specific.
- B) Snowflake (using `CLONE`) and Databricks (using shallow clone) — these support zero-copy cloning natively.
- C) Only Snowflake supports zero-copy cloning in dbt.
- D) Snowflake, Databricks, and Redshift all support zero-copy cloning.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Zero-copy cloning is a **warehouse feature**, not a dbt feature. It is only available on platforms that natively support it. |
> | **B) ✅ Correct** | **Snowflake** supports zero-copy cloning via the `CLONE` command — it creates metadata pointers with no data movement. **Databricks** supports it via **shallow clone** on Delta tables. BigQuery supports table clone (also zero-copy). On platforms that don't support native cloning (Redshift, Postgres), `dbt clone` falls back to creating **pointer views** (`SELECT * FROM source`) — no data copy, but also no independent data — rather than physical clones. |
> | **C) ❌ Incorrect** | Databricks also supports zero-copy cloning via shallow clone, and BigQuery supports table clone. |
> | **D) ❌ Incorrect** | Redshift does **not** support zero-copy cloning. `dbt clone` on Redshift falls back to pointer views. |
>
> > 💡 **Key rule**: Zero-copy clone: Snowflake (`CLONE`), Databricks (shallow clone), BigQuery (table clone). Redshift/Postgres = pointer views (no native clone).

---

### Q16.
> **Subdomain 4c.16 — dbt clone fallback behavior**

A team uses `dbt clone` to populate their green environment on a **Postgres** warehouse. After the clone command runs, they notice the cloned models are simple views pointing to the source tables rather than independent copies. They expected separate physical tables. Why did this happen?

- A) `dbt clone` always creates views — it never creates physical copies regardless of platform.
- B) Postgres does not support native zero-copy table cloning, so `dbt clone` falls back to creating **pointer views** (`SELECT * FROM source_table`) in the target schema.
- C) The `--full-refresh` flag was missing, causing dbt to create views instead of tables.
- D) dbt clone creates views until the `--materialize` flag is passed.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | On platforms that support native cloning (Snowflake, Databricks), `dbt clone` creates actual zero-copy clones, not views. |
> | **B) ✅ Correct** | Postgres (and Redshift) do not support native zero-copy table cloning. On these platforms, `dbt clone` automatically **falls back to creating pointer views** — simple `CREATE VIEW AS SELECT * FROM <source>` statements. The views point to the original production tables, so they reflect production data but are not independent copies. This is important to understand: cloned "data" on Postgres is actually just pass-through views. |
> | **C) ❌ Incorrect** | `--full-refresh` controls whether existing relations are recreated, not whether they become tables vs views. |
> | **D) ❌ Incorrect** | There is no `--materialize` flag for `dbt clone`. |
>
> > 💡 **Key rule**: `dbt clone` on Redshift/Postgres = pointer views (not physical copies). On Snowflake/Databricks = true zero-copy clones.

---

### Q17.
> **Subdomain 4c.17 — dbt clone includes defer**

A team runs `dbt clone --select "tag:finance" --state ./prod_artifacts` to populate only the finance models in their green environment. They notice that upstream models NOT tagged `finance` are automatically resolved against production rather than being cloned. Why?

- A) `dbt clone` only processes selected nodes — upstream models outside the selection are ignored entirely and cause resolution errors.
- B) `dbt clone` automatically includes `--defer` behavior — unselected upstream nodes are resolved against the source state (production) rather than being cloned.
- C) The `--state` flag automatically applies deferral to all unselected nodes as a separate mechanism from `dbt clone`.
- D) This behavior requires explicitly passing `--defer` alongside `dbt clone`.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Unselected upstream nodes do not cause errors — they are resolved against the source state automatically. |
> | **B) ✅ Correct** | `dbt clone` **automatically includes `--defer` behavior** — it is built in. When you clone a subset of models, any upstream nodes that were not selected are automatically resolved against the source state (production) rather than being cloned or failing. You do not need to explicitly add `--defer`. This makes partial clone operations safe and efficient. |
> | **C) ❌ Incorrect** | The `--state` flag provides the comparison manifest; it does not by itself apply deferral. The deferral is built into `dbt clone`'s default behavior. |
> | **D) ❌ Incorrect** | `--defer` is already included in `dbt clone` implicitly. Adding it explicitly is redundant but not harmful. |
>
> > 💡 **Key rule**: `dbt clone` auto-includes `--defer` — unselected upstream nodes resolve against source state automatically.

---

### Q18.
> **Subdomain 4c.18 — Partial run before swap**

An on-call engineer is under pressure to deploy a hotfix quickly. Instead of running the full dbt job, they run `dbt run --select state:modified` to rebuild only the changed models in the green environment, then immediately trigger `swap_database`. What is the risk?

- A) None — running only modified models is a valid optimization for blue/green deployments.
- B) The green environment will be incomplete — unmodified models in green may be stale or missing, so after the swap, production serves a mix of new and old data.
- C) The `swap_database` operation will fail if the green environment is incomplete.
- D) The partial run means only the modified models get tested before the swap, but the overall risk is low if the modified models pass.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Partial runs before a swap are explicitly called out as a risk in the blue/green pattern. |
> | **B) ✅ Correct** | `swap_database` swaps the **entire green database** to production — not just the modified models. If green was only partially rebuilt, the swapped production environment will contain a mix of newly-built models and whatever stale or missing models existed in green from prior deployments. The swap itself always succeeds (it's just a metadata operation), but the resulting production state may be inconsistent. **Only trigger `swap_database` after a full `dbt run`** covering all models. |
> | **C) ❌ Incorrect** | `swap_database` is a metadata operation that doesn't validate whether green is complete. It will execute regardless. |
> | **D) ❌ Incorrect** | The risk is not low — downstream models in green that weren't rebuilt may reference stale data after the swap. |
>
> > 💡 **Key rule**: Never swap after a partial run. `swap_database` promotes the entire green database — if green is incomplete, production becomes inconsistent.

---

### Q19.
> **Subdomain 4c.19 — Failure safety**

A blue/green deployment job runs `dbt run` in the green environment, then `dbt test`. Five tests fail. The job is configured to run `dbt run-operation swap_database` as the final step. What happens to the production (blue) environment?

- A) The swap proceeds anyway — the test failures are logged but do not block the swap step.
- B) Production (blue) remains live and untouched — because `dbt test` failed, dbt Cloud stops the job before the `swap_database` step executes.
- C) Production (blue) is rolled back to its state from before the green build started.
- D) The swap proceeds for models whose tests passed; only the failed models are excluded from the swap.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Test failures are not just logged — they cause the job step to fail, which stops subsequent steps from executing. |
> | **B) ✅ Correct** | dbt Cloud job commands run **sequentially** — a failure at any step stops all subsequent steps. If `dbt test` fails, the job stops immediately. The `dbt run-operation swap_database` step never executes. Production (blue) remains **completely untouched and live**. This is one of the key safety properties of blue/green: failure is safe by design. |
> | **C) ❌ Incorrect** | Blue was never modified during the green build — there is nothing to roll back. Blue has been live and unchanged throughout. |
> | **D) ❌ Incorrect** | `swap_database` is an all-or-nothing operation — it swaps the entire database. There is no selective per-model swap. |
>
> > 💡 **Key rule**: Blue/green failure is safe — test failures stop the job before swap executes. Blue production stays live and untouched.

---

### Q20. ⭐
> **Subdomain 4c.20 — Recommended job sequence**

Which of the following represents the **correct recommended command sequence** for a blue/green deployment job in dbt Cloud?

- A) `dbt run-operation swap_database` → `dbt run` → `dbt test`
- B) `dbt test` → `dbt run` → `dbt run-operation swap_database`
- C) `dbt run` → `dbt run-operation swap_database` → `dbt test`
- D) `dbt run` → `dbt test` → `dbt run-operation swap_database`

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Swapping before building is catastrophically wrong — production would be swapped to an empty or stale green environment before any models run. |
> | **B) ❌ Incorrect** | Running tests before building models means testing against the previous state in green, not the newly-built models. |
> | **C) ❌ Incorrect** | Swapping before testing means production is promoted to green before quality is validated. If tests subsequently fail, production already has the potentially bad data. |
> | **D) ✅ Correct** | The recommended sequence is: (1) **`dbt run`** — build all models in the green environment; (2) **`dbt test`** — validate all data quality tests against the freshly-built green data; (3) **`dbt run-operation swap_database`** — only after tests pass, atomically swap green to production. This ensures production is only ever promoted to a tested, complete state. |
>
> > 💡 **Key rule**: Blue/green sequence = `dbt run` → `dbt test` → `dbt run-operation swap_database`. Never swap before tests pass.

---

*[End of Topic 4c — 20 questions]*

