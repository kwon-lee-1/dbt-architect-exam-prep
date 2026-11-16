# Topic 9: Hooks & Operations — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 20 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 9.1 — Post-hook transaction behavior on model failure**

On Postgres, a post-hook is configured to insert a row into an audit table every time a model completes. The model fails mid-execution due to a bad SQL statement. Does the audit row get inserted?

- A) Yes — but the audit row is marked with a "failed" status code automatically.
- B) Yes — post-hooks run regardless of model success or failure to ensure audit completeness.
- C) No — post-hooks are skipped when a model fails, but dbt logs the skipped hook in the run results.
- D) No — by default, post-hooks run inside the model's transaction. When the model fails, the transaction rolls back before the post-hook executes.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt has no mechanism to automatically mark audit rows with failure status from within the transaction — and the hook doesn't run at all on failure anyway. |
> | **B) ❌ Incorrect** | Post-hooks do not automatically run on failure — they are part of the same transaction that rolls back. |
> | **C) ❌ Incorrect** | While dbt does track skipped hooks, the core issue is that the hook doesn't run — the log detail is secondary. |
> | **D) ✅ Correct** | On transactional adapters (the docs name Postgres and Redshift), `pre-hook` and `post-hook` run **inside the model's transaction** by default. When the model fails, the transaction rolls back — and since the post-hook is part of that transaction, it **never executes**. Fix: add `transaction: false` to the hook definition so it runs outside the transaction and persists even when the model fails: `post_hook: {sql: "INSERT INTO audit...", transaction: false}`. |
>
> > 💡 **Key rule**: Post-hook default = **inside transaction**. Model failure = transaction rollback = hook skipped. Use `transaction: false` for audit logging.

---

### Q2. ⭐
> **Subdomain 9.2 — Post-hook failure rolls back model**

On Postgres, a post-hook runs a `GRANT SELECT` statement after a model builds. The role name in the grant is misspelled, causing the grant to fail. What happens to the model that was just built?

- A) The model's creation is rolled back — since the post-hook runs inside the transaction, its failure rolls back the entire transaction including the model.
- B) The model remains built but is flagged as "degraded" in the dbt Catalog health signals.
- C) Only the post-hook is retried — the model itself is not affected.
- D) The model remains built — post-hook failures are isolated and don't affect model creation.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | On Postgres and Redshift, hooks run inside the same transaction as the model build, so a failing hook fails the transaction and the model build is rolled back too. Use `transaction: false` if the hook must not affect the build. |
> | **B) ❌ Incorrect** | There is no "degraded" status for post-hook failures in dbt Catalog. |
> | **C) ❌ Incorrect** | dbt does not automatically retry post-hooks. |
> | **D) ❌ Incorrect** | This is the opposite of the actual behavior — post-hook failures within a transaction are not isolated. |
>
> > 💡 **Key rule**: Post-hook failure (inside transaction) = **model rollback too**. Use `transaction: false` for non-critical post-hooks.

---

### Q3. ⭐
> **Subdomain 9.3 — {{ results }} context variable**

A team adds a post-hook to a model that uses `{{ results }}` to log the outcome:

```yaml
post_hook: "INSERT INTO run_log VALUES ({{ results }})"
```

The hook runs without errors but `results` is always `None`. Why?

- A) `{{ results }}` is populated only after the first model in a run completes — a single-model run always returns `None`.
- B) `{{ results }}` must be called as `{{ this.results }}` within a post-hook context.
- C) `{{ results }}` is **only available in `on-run-end` hooks** — it returns `None` silently in `pre-hook` and `post-hook`.
- D) `{{ results }}` requires the `on-run-end` hook to be configured first before it's populated in post-hooks.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The number of models in a run has no bearing on `results` availability — the issue is the hook type, not run size. |
> | **B) ❌ Incorrect** | `{{ this.results }}` is not valid syntax — `results` is a separate top-level variable, not an attribute of `this`. |
> | **C) ✅ Correct** | `{{ results }}` is **only available in `on-run-end` hooks** — it returns `None` in `pre-hook` and `post-hook` with no error or warning. This is a silent failure that can be hard to debug. The correct approach: use `{{ this }}` in post-hooks to reference the current model relation, and use `{{ results }}` only in `on-run-end` to access all run outcomes. |
> | **D) ❌ Incorrect** | `on-run-end` is independent — it doesn't "unlock" `results` for post-hooks. |
>
> > 💡 **Key rule**: `{{ results }}` = **`on-run-end` only**. In pre/post-hook = `None` (silent). Use `{{ this }}` in post-hooks.

---

### Q4.
> **Subdomain 9.4 — Multiple hooks accumulate**

A model has 2 post-hooks defined in `dbt_project.yml` and 3 post-hooks defined in the model's `config()` block. How many post-hooks execute when the model runs?

- A) 3 — model-level `config()` hooks override project-level hooks.
- B) 5 — all hooks from all scopes accumulate and execute in order.
- C) 2 — dbt deduplicates identical hooks automatically.
- D) 2 — project-level hooks take precedence over model-level hooks.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Model-level hooks do NOT override project-level hooks — they accumulate. |
> | **B) ✅ Correct** | Hooks from **all scopes accumulate** — they do not override each other. All 5 post-hooks execute: first the 2 project-level hooks (in definition order), then the 3 model-level `config()` block hooks (in definition order). Execution order: package → `dbt_project.yml` → `config()` block. Within each scope: top-to-bottom. |
> | **C) ❌ Incorrect** | dbt doesn't deduplicate hooks. |
> | **D) ❌ Incorrect** | Project-level hooks do NOT override model-level hooks either — all execute. |
>
> > 💡 **Key rule**: Hooks **accumulate** across scopes — they never override. All hooks from all scopes execute in scope order.

---

### Q5. ⭐
> **Subdomain 9.5 — VACUUM on Redshift: transaction: false**

A Redshift post-hook is designed to run `VACUUM SORT ONLY` after each model builds. The hook fails with a database error. What is the most likely cause and fix?

- A) Redshift doesn't support `VACUUM` commands in dbt hooks — use `dbt run-operation` instead.
- B) `VACUUM SORT ONLY` syntax is deprecated in Redshift — use `VACUUM FULL` instead.
- C) Post-hooks can't run multi-word SQL commands — split the command into a macro.
- D) `VACUUM` on Redshift cannot run inside a transaction. Add `transaction: false` to the hook so it runs outside the model's transaction.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `VACUUM` can be used in dbt hooks — the issue is transaction context, not hook type. Using `dbt run-operation` would work but isn't required. |
> | **B) ❌ Incorrect** | `VACUUM SORT ONLY` is valid Redshift syntax — it's not deprecated. |
> | **C) ❌ Incorrect** | Multi-word SQL is valid in hook definitions. |
> | **D) ✅ Correct** | **Redshift's `VACUUM` command cannot run inside a transaction**, which the docs give as a reason to use `transaction: false`. By default, post-hooks run inside the model's transaction. Fix: `post_hook: {sql: "VACUUM SORT ONLY {{this}}", transaction: false}`. The `transaction: false` flag runs the hook outside the transaction. |
>
> > 💡 **Key rule**: Redshift `VACUUM` cannot run inside a transaction. Use `transaction: false` in the post-hook definition.

---

### Q6.
> **Subdomain 9.6 — on-run-end fires on partial failure**

A run includes 20 models. 3 models fail. An `on-run-end` hook is configured to send a Slack notification summarizing the run. Does the `on-run-end` hook fire?

- A) Yes — but only if the `on-run-end` hook is defined with `transaction: false`.
- B) No — `on-run-end` is skipped when any model fails to prevent sending false success notifications.
- C) No — `on-run-end` only fires when the run completes successfully (all models pass).
- D) Yes — `on-run-end` fires after the run completes regardless of partial failures. The `results` variable contains entries for all resources including failures.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `on-run-end` is not subject to model transaction context — it runs at the project level outside model transactions. `transaction: false` is relevant for `pre-hook`/`post-hook`, not `on-run-end`. |
> | **B) ❌ Incorrect** | Suppressing `on-run-end` on failure would defeat its main use case (alerting on failures). |
> | **C) ❌ Incorrect** | `on-run-end` fires after the run regardless of success or failure — partial failure doesn't suppress it. |
> | **D) ✅ Correct** | `on-run-end` runs at the end of the command. `results` has one Result object per resource that executed, and the docs example shows an `error` result next to a `success` one. Filter on `res.status` to report failures. |
>
> > 💡 **Key rule**: `on-run-end` runs at the end of the command, and `results` includes failed resources. Filter on `res.status`.

---

### Q7.
> **Subdomain 9.7 — on-run-start and on-run-end configuration location**

A developer wants to add an `on-run-start` hook to resume a Snowflake warehouse before any models run. They add the hook to a model's `config()` block. The hook never fires. Why?

- A) `on-run-start` and `on-run-end` can only be configured in `dbt_project.yml` — they cannot be set in model `config()` blocks or YAML property files.
- B) `on-run-start` requires the `transaction: false` flag to fire correctly.
- C) `on-run-start` hooks only fire when running `dbt run` — not `dbt build` or other commands.
- D) The Snowflake warehouse resume command must use a specific macro format to work in hooks.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | `on-run-start` and `on-run-end` are **project-level hooks** and can **only be configured in `dbt_project.yml`**. They cannot be defined in model `config()` blocks or YAML property files — those locations only support `pre-hook` and `post-hook`. This is a common mistake when developers confuse the scope of different hook types. |
> | **B) ❌ Incorrect** | `transaction: false` is relevant for post-hooks that run SQL that can't be in a transaction — it has nothing to do with `on-run-start` configuration location. |
> | **C) ❌ Incorrect** | `on-run-start` fires once per dbt command — this includes `dbt run`, `dbt build`, `dbt test`, `dbt seed`, `dbt snapshot`, `dbt compile`, and `dbt docs generate`. |
> | **D) ❌ Incorrect** | The macro format is a separate concern — the root issue is where the hook is configured. |
>
> > 💡 **Key rule**: `on-run-start`/`on-run-end` = **`dbt_project.yml` only**. Cannot be set in model `config()` blocks or YAML files.

---

### Q8.
> **Subdomain 9.8 — Seeds and hook configuration**

A team wants to add a post-hook to a seed file to grant SELECT privileges to a reporter role after each seed load. Where must this post-hook be configured?

- A) In the seed CSV file's header row using a special dbt comment format.
- B) In the seed file's corresponding `.yml` property file or in `dbt_project.yml` — seeds do not support in-file `config()` blocks.
- C) In the model's `config()` block (any `.sql` file that references the seed).
- D) In `profiles.yml` under the seed's connection configuration.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Seed CSV files are plain data files — they have no mechanism for dbt config comments or headers. |
> | **B) ✅ Correct** | Seeds are CSV files — they **cannot have in-file `config()` blocks** (that syntax is for `.sql` model files). Hooks for seeds must be configured either in `dbt_project.yml` (project-level) or in a YAML property file (e.g., `seeds/schema.yml`). Both approaches attach the hook to the seed without needing a SQL file. |
> | **C) ❌ Incorrect** | You cannot configure a hook for a seed in a model's `config()` block — that block applies to the specific SQL model file, not referenced seeds. |
> | **D) ❌ Incorrect** | `profiles.yml` contains connection configuration — hooks are not configured there. |
>
> > 💡 **Key rule**: Seeds = no in-file `config()` block (CSV files). Seed hooks → `dbt_project.yml` OR YAML property file only.

---

---

### Q9.
> **Subdomain 9.9 — transaction: false syntax**

A team needs an audit log row to persist even when the model it's associated with fails. They currently use a standard post-hook but the audit row is never inserted on failure. What is the correct hook syntax to run the SQL outside the model's transaction?

- A) Use `on-run-end` instead of `post-hook` — it always runs outside transactions.
- B) Add `no_transaction: true` to the hook string.
- C) Use dictionary syntax: `{sql: "INSERT INTO audit_log ...", transaction: false}`.
- D) Call the hook with `--no-transaction` flag in the dbt command.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `on-run-end` fires after the full run completes and is unrelated to individual model transaction behavior. Using it for per-model audit rows would require inspecting `results` to find which models ran, which is more complex. |
> | **B) ❌ Incorrect** | `no_transaction: true` is not valid hook syntax. |
> | **C) ✅ Correct** | To run a hook **outside the model's transaction**, use the **dictionary syntax** with `transaction: false`: `post_hook: {sql: "INSERT INTO audit_log VALUES (...)", transaction: false}`. Without this, post-hooks run inside the model's transaction — if the model fails, the transaction rolls back and the hook never executes. The docs name two typical uses: `VACUUM` on Redshift, and an audit record that should persist even if the build fails. Don't use it on Snowflake, BigQuery, Spark or Databricks, where dbt doesn't use transactions. `before_begin()` / `after_commit()` are helper-macro alternatives. |
> | **D) ❌ Incorrect** | There is no `--no-transaction` CLI flag in dbt. |
>
> > 💡 **Key rule**: Hook outside transaction = `{sql: "...", transaction: false}`. Required for audit logs, VACUUM, and any SQL that must persist even when the model fails.

---

### Q10.
> **Subdomain 9.10 — Hook execution order across scopes**

A dbt project has the following hooks configured:
- A package defines a `post-hook` for a model
- `dbt_project.yml` defines 2 `post-hook` entries
- The model's `config()` block defines 1 `post-hook`

In what order do these post-hooks execute when the model runs?

- A) dbt_project.yml → config() block → package (alphabetical by scope name)
- B) config() block first → dbt_project.yml → package (model-level takes priority)
- C) Package → dbt_project.yml → config() block (outer scope first, inner scope last)
- D) All hooks run in random order — the order is not guaranteed

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Alphabetical by scope name is not the ordering rule. |
> | **B) ❌ Incorrect** | Model-level hooks do not take priority — they run last, not first. |
> | **C) ✅ Correct** | Hook execution order flows from **outermost to innermost scope**: (1) **Package-level hooks** run first; (2) **`dbt_project.yml` project-level hooks** run second; (3) **Model `config()` block / YAML property file hooks** run last. Within the same scope, hooks execute in **definition order** (top to bottom). All hooks from all scopes accumulate — model-level hooks never override project-level hooks. |
> | **D) ❌ Incorrect** | The order is deterministic and documented — it is not random. |
>
> > 💡 **Key rule**: Hook order = **package → dbt_project.yml → config() block**. All hooks accumulate — none override others.

---

### Q11.
> **Subdomain 9.11 — {{ this }} context variable**

A post-hook needs to run a GRANT statement after a Snowflake model builds, granting SELECT to a reporter role on the exact table/view that was just created. Which context variable provides the fully-qualified relation object for the current model?

- A) `{{ model.name }}` — the model's identifier
- B) `{{ target.schema }}.{{ model.name }}` — constructed from target and model name
- C) `{{ node.relation_name }}` — the canonical relation reference
- D) `{{ this }}` — the relation object for the current model (database.schema.identifier)

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `{{ model.name }}` is just the model identifier string — it does not include database or schema, so it cannot be used in a GRANT statement that needs a fully-qualified reference. |
> | **B) ❌ Incorrect** | While this could work in simple cases, it is fragile and not idiomatic. `{{ this }}` handles quoting and qualification correctly. |
> | **C) ❌ Incorrect** | `{{ node.relation_name }}` is not a documented standard context variable for hooks. |
> | **D) ✅ Correct** | **`{{ this }}`** is the **relation object** for the current model — it resolves to the fully-qualified `database.schema.identifier` in the compiled hook SQL. It is available in both `pre-hook` and `post-hook`. The docs use `{{ this }}` in their hook examples, such as `analyze table {{ this }} ...`. |
>
> > 💡 **Key rule**: `{{ this }}` = fully-qualified relation object in pre/post-hooks.

---

### Q12.
> **Subdomain 9.12 — on-run-end context variables**

An `on-run-end` hook needs to report two things: (1) which schemas were written to during the run, and (2) a list of results for every resource that ran. Which context variables provide these?

- A) `{{ schemas }}` (list of schemas) and `{{ results }}` (list of result objects for every resource)
- B) `{{ this }}` and `{{ results }}`
- C) `{{ target.schema }}` and `{{ results }}`
- D) `{{ database_schemas }}` and `{{ run_results }}`

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Two `on-run-end`-specific variables: **`{{ schemas }}`** — a list of all schemas written to during the run (useful for generating per-schema grants or reports). **`{{ results }}`** — a list of result objects for every resource that ran, each with `res.node.unique_id`, `res.status`, and `res.message`. Additionally, `{{ database_schemas }}` provides (database, schema) tuples for cross-database runs. These variables are ONLY available in `on-run-end` — they return `None` in pre-hook or post-hook. |
> | **B) ❌ Incorrect** | `{{ this }}` is a pre/post-hook variable representing the current model — it is not available in `on-run-end`. |
> | **C) ❌ Incorrect** | `{{ target.schema }}` is the primary target schema, not the full list of all schemas written to during the run. |
> | **D) ❌ Incorrect** | `{{ run_results }}` is not the documented variable name — it is `{{ results }}`. |
>
> > 💡 **Key rule**: `on-run-end` variables: `{{ schemas }}` (list of schemas), `{{ results }}` (list of result objects), `{{ database_schemas }}` (tuples). All return `None` in pre/post-hooks.

---

### Q13.
> **Subdomain 9.13 — Operations require run_query**

A developer writes a macro to clean up temporary tables:
```sql
{% macro cleanup_temp_tables() %}
  DROP TABLE IF EXISTS {{ target.schema }}.tmp_staging;
{% endmacro %}
```
They run `dbt run-operation cleanup_temp_tables`. The command succeeds but the table is still there. Why?

- A) `DROP TABLE` requires a separate `--force` flag when called via `run-operation`.
- B) The macro must use `run_query()` or a `{% call statement() %}` block to execute SQL — simply returning a SQL string from a macro does not execute it.
- C) Macros called via `run-operation` run in read-only mode by default.
- D) `dbt run-operation` can only call macros that are in the `macros/` directory, not in `models/`.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no `--force` flag for `dbt run-operation`. |
> | **B) ✅ Correct** | A macro called via `dbt run-operation` does **not** auto-execute SQL simply by returning a string. The macro must explicitly execute SQL using **`run_query()`** or a `{% call statement() %}` block. A macro that just templates SQL as a return value produces no warehouse side effect. Fix: `{% do run_query("DROP TABLE IF EXISTS " ~ target.schema ~ ".tmp_staging") %}`. |
> | **C) ❌ Incorrect** | `run-operation` macros run with full write access to the warehouse — there is no read-only default mode. |
> | **D) ❌ Incorrect** | Macros for `run-operation` are in the `macros/` directory — this is correct. Location is not the issue. |
>
> > 💡 **Key rule**: Operations don't auto-execute SQL return values. Must use `run_query()` or `{% call statement() %}` to actually execute SQL.

---

### Q14.
> **Subdomain 9.14 — dbt run-operation syntax**

A macro named `grant_schema_access` accepts two parameters: `role` and `schema_name`. How is this macro correctly invoked using `dbt run-operation`?

- A) `dbt run-operation grant_schema_access --params '{"role": "analyst", "schema_name": "core"}'`
- B) `dbt run-operation grant_schema_access --args '{role: analyst, schema_name: core}'`
- C) `dbt run-operation grant_schema_access role=analyst schema_name=core`
- D) `dbt run-operation --macro grant_schema_access --args role=analyst --args schema_name=core`

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The flag is `--args`, not `--params`. |
> | **B) ✅ Correct** | `dbt run-operation` passes arguments via the **`--args` flag** as a **YAML dictionary**: `dbt run-operation grant_schema_access --args '{role: analyst, schema_name: core}'`. Both YAML and JSON dict formats are accepted. The keys must exactly match the macro's parameter names. |
> | **C) ❌ Incorrect** | Positional or keyword arguments passed directly after the macro name are not valid syntax for `dbt run-operation`. |
> | **D) ❌ Incorrect** | The `--macro` flag does not exist. The macro name is a positional argument directly after `run-operation`. |
>
> > 💡 **Key rule**: `dbt run-operation <macro_name> --args '{key: value, key2: value2}'`. Args as YAML/JSON dict. Keys match macro parameter names exactly.

---

### Q15.
> **Subdomain 9.15 — Operations vs hooks**

A team needs to grant `SELECT` on all tables in the production schema to a `reporter` role. This grant must run once after each **full** deployment job (not per model). They are deciding between a `post-hook` and a `dbt run-operation`. Which approach is more appropriate and why?

- A) An `on-run-end` hook in `dbt_project.yml` — it fires once per dbt command, granting on all schemas after the job completes.
- B) A `post-hook` on every model — this grants per table as each model builds.
- C) Either approach works identically — the choice is stylistic.
- D) A `dbt run-operation` step added to the job's command list — it is explicitly invoked once after the build completes, running an ad-hoc grant across all tables.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | An **`on-run-end` hook** configured in `dbt_project.yml` fires **once per dbt command** — after all models have built. It can run `GRANT SELECT ON ALL TABLES IN SCHEMA {{ target.schema }} TO ROLE reporter` in a single statement. The docs show `on-run-end` hooks granting at the end of a run (for example looping over `schemas`). It runs automatically with every command, with no extra job step. A `run-operation` step also works but is invoked manually. |
> | **B) ❌ Incorrect** | Per-model post-hooks grant per table as each model builds — this works but means hundreds of individual GRANT statements rather than one bulk grant. |
> | **C) ❌ Incorrect** | The approaches differ in automation (hooks are automatic) vs explicitness (operations are manual command steps). |
> | **D) ❌ Incorrect** | Works, but it's a manual step you must add to each job. Operations fit one-off tasks. |
>
> > 💡 **Key rule**: Use `on-run-end` for automated run-level tasks (once per job). Use `run-operation` for ad-hoc or one-time commands.

---

### Q16.
> **Subdomain 9.16 — on-run-start/end fire frequency**

A team configures an `on-run-start` hook to log the run start time to an audit table. They run `dbt build` which executes 50 models. How many times does the `on-run-start` hook fire?

- A) 50 times — once per model
- B) 2 times — once at the start of `dbt run` and once at the start of `dbt test` (since `dbt build` internally executes both)
- C) 0 times — `on-run-start` only fires for `dbt run`, not `dbt build`
- D) 1 time — once per dbt command invocation

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `on-run-start` fires once per command invocation — not per model. Per-model execution is for `pre-hook`/`post-hook`. |
> | **B) ❌ Incorrect** | `dbt build` is a single command invocation — it does not fire separate `on-run-start` hooks for its internal run and test phases. |
> | **C) ❌ Incorrect** | `on-run-start` fires for `dbt build`, `dbt run`, and all other resource-executing dbt commands. |
> | **D) ✅ Correct** | `on-run-start` fires **once per dbt command invocation** — regardless of how many models are in the run. For `dbt build` with 50 models, it fires exactly **once**. The same applies to `on-run-end`. These are project-level hooks, not resource-level. Also note: `on-run-start`/`on-run-end` fire for **every dbt command** that executes project resources — `dbt run`, `dbt build`, `dbt test`, `dbt seed`, `dbt snapshot`, `dbt compile`, `dbt docs generate`. |
>
> > 💡 **Key rule**: `on-run-start`/`on-run-end` = once per dbt command, not per model. Fires for all resource-executing commands (run, build, test, seed, snapshot, compile).

---

### Q17.
> **Subdomain 9.17 — Grants: config vs hooks**

A data platform team wants every model in the project granted `SELECT` to a `reporter` role after it builds. What do the docs recommend?

- A) A `post-hook` in every model's `config()` block.
- B) `on-run-end` with `schemas` to grant on each schema.
- C) The `grants` resource config in `dbt_project.yml`, e.g. `+grants: {select: ['reporter']}`.
- D) A `dbt run-operation` step in every job.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Needs a change in every model, and the docs prefer the `grants` config. |
> | **B) ❌ Incorrect** | A valid hook pattern, but it's not what the docs recommend when the `grants` config can do the job. |
> | **C) ✅ Correct** | The docs say to define grants as resource configs whenever possible. dbt makes the grants match exactly, revoking grantees you didn't list. |
> | **D) ❌ Incorrect** | Manual step in every job. |
>
> > 💡 **Key rule**: Grants → `grants` config first. Post-hooks only for what it can't do (masking or row access policies, future grants, objects other than tables and views, Databricks `READ_METADATA`/`USAGE`).

---

### Q18.
> **Subdomain 9.18 — Calling macros from hooks**

A team has a macro `my_grant(relation, role)` that generates a GRANT statement. They want to call it from a `post-hook` on a model. What is the correct hook syntax?

- A) `post_hook: "{{ my_grant({{ this }}, 'reporter') }}"`
- B) `post_hook: "my_grant(this, 'reporter')"`
- C) `post_hook: my_grant(this, 'reporter')`
- D) `post_hook: "{{ my_grant(this, 'reporter') }}"`

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `{{ {{ this }} }}` is invalid nested Jinja — it causes a compilation error. `this` inside a Jinja expression does not need extra `{{ }}`. |
> | **B) ❌ Incorrect** | Without Jinja delimiters (`{{ }}`), the string is passed literally without macro evaluation. |
> | **C) ❌ Incorrect** | Without Jinja delimiters, this is a literal string, not a macro call. |
> | **D) ✅ Correct** | Hooks are strings evaluated as Jinja templates. To call a macro, wrap the entire call in Jinja: `"{{ my_grant(this, 'reporter') }}"`. The outer `{{ }}` tells dbt to evaluate the Jinja expression. Inside, `this` is the relation context variable (no extra curly braces needed). dbt evaluates the hook string as Jinja at runtime, calls `my_grant(this, 'reporter')`, and executes the returned SQL. |
>
> > 💡 **Key rule**: Macro call in hook = `"{{ macro_name(this, 'arg') }}"`. `this` inside `{{ }}` needs no additional delimiters.

---

### Q19.
> **Subdomain 9.19 — Hook accumulation**

A project uses a dbt package that defines a `post-hook` on all models. The `dbt_project.yml` also defines a `post-hook`. A model's `config()` block additionally defines a `post-hook`. A developer expects the model-level `config()` hook to override and replace the others. What actually happens?

- A) The model-level `config()` hook overrides all others — only the model's config() hook runs.
- B) The package hook is disabled when `dbt_project.yml` defines any hook, regardless of model config.
- C) All three post-hooks run — hooks from all scopes **accumulate**, and no scope overrides another.
- D) The `dbt_project.yml` hook overrides the package hook, and the config() hook overrides both — only one hook runs.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Model-level hooks do not override higher-scope hooks — they add to them. |
> | **B) ❌ Incorrect** | Package hooks are not disabled by project-level hook definitions. |
> | **C) ✅ Correct** | Hooks in dbt **accumulate across all scopes** — they do not override each other. All three hooks run: the package hook, the `dbt_project.yml` hook, and the model's `config()` hook. They execute in order: package → project.yml → config() block. If you have 3 hooks at project level and 2 at model level, all 5 execute. This is an important distinction from how configs work in dbt (where more specific configs override less specific ones). Hooks are additive, not override-based. |
> | **D) ❌ Incorrect** | No hook scope overrides another. They all accumulate. |
>
> > 💡 **Key rule**: Hooks **accumulate** — they never override. All hooks from all scopes run. Configs override; hooks add.

---

### Q20.
> **Subdomain 9.20 — on-run-end results object**

An `on-run-end` hook sends a summary notification. A developer needs to count how many models succeeded and how many errored. They use `{{ results }}` in the hook. What is the structure of each object in `results`, and how do they filter for errors?

- A) `results` is a dictionary keyed by model name — access error status with `results['model_name']['status']`.
- B) Each result object has `res.node.unique_id`, `res.status` (values: `success`, `error`, `skipped`), and `res.message`. Filter errors with `{% if res.status == 'error' %}`.
- C) Each result has `res.model` (name) and `res.passed` (boolean) — filter with `{% if not res.passed %}`.
- D) Each result is a string like `"model_name: success"` — filter with `if 'error' in res`.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `results` is a list, not a dictionary. Access is by iteration, not by key. |
> | **B) ✅ Correct** | Each object in `{{ results }}` has: **`res.node.unique_id`** (e.g., `model.project.model_name`), **`res.status`** (the docs example shows `success` and `error`), and **`res.message`** (error or completion message). To count errors: `{% set error_count = results | selectattr("status", "equalto", "error") | list | length %}`. The results list includes all resources that ran, even partial failures — making it ideal for run-level reporting in `on-run-end`. |
> | **C) ❌ Incorrect** | `res.passed` is not a documented property. The status field uses string values, not a boolean. |
> | **D) ❌ Incorrect** | Results are not string values. They are structured objects with named properties. |
>
> > 💡 **Key rule**: `results` list — each item has `res.node.unique_id`, `res.status`, `res.message`. Filter: `selectattr("status", "equalto", "error")`.

---

*[End of Topic 9 — 20 questions]*

