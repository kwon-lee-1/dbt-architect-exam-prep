# Topic 9: Hooks & Operations — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 20 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 9.1 — Post-hook transaction behavior on model failure**

A post-hook is configured to insert a row into an audit table every time a model completes. The model fails mid-execution due to a bad SQL statement. Does the audit row get inserted?

- A) Yes — post-hooks run regardless of model success or failure to ensure audit completeness.
- B) No — by default, post-hooks run inside the model's transaction. When the model fails, the transaction rolls back before the post-hook executes.
- C) Yes — but the audit row is marked with a "failed" status code automatically.
- D) No — post-hooks are skipped when a model fails, but dbt logs the skipped hook in the run results.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Post-hooks do not automatically run on failure — they are part of the same transaction that rolls back. |
> | **B) ✅ Correct** | By default, `pre-hook` and `post-hook` run **inside the model's transaction**. When the model fails, the transaction rolls back — and since the post-hook is part of that transaction, it **never executes**. Fix: add `transaction: false` to the hook definition so it runs outside the transaction and persists even when the model fails: `post_hook: {sql: "INSERT INTO audit...", transaction: false}`. |
> | **C) ❌ Incorrect** | dbt has no mechanism to automatically mark audit rows with failure status from within the transaction — and the hook doesn't run at all on failure anyway. |
> | **D) ❌ Incorrect** | While dbt does track skipped hooks, the core issue is that the hook doesn't run — the log detail is secondary. |
>
> > 💡 **Key rule**: Post-hook default = **inside transaction**. Model failure = transaction rollback = hook skipped. Use `transaction: false` for audit logging.

---

### Q2. ⭐
> **Subdomain 9.2 — Post-hook failure rolls back model**

A post-hook runs a `GRANT SELECT` statement after a model builds. The role name in the grant is misspelled, causing the grant to fail. What happens to the model that was just built?

- A) The model remains built — post-hook failures are isolated and don't affect model creation.
- B) The model's creation is rolled back — since the post-hook runs inside the transaction, its failure rolls back the entire transaction including the model.
- C) The model remains built but is flagged as "degraded" in the dbt Catalog health signals.
- D) Only the post-hook is retried — the model itself is not affected.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This is the opposite of the actual behavior — post-hook failures within a transaction are not isolated. |
> | **B) ✅ Correct** | Since post-hooks run inside the model's transaction by default, a post-hook failure **causes the entire transaction to roll back** — including the model creation itself. The model is dropped. This is a double-edged sword: the transaction guarantees atomicity but means post-hook failures can undo completed model builds. Escape this behavior with `transaction: false` if the post-hook is non-critical. |
> | **C) ❌ Incorrect** | There is no "degraded" status for post-hook failures in dbt Catalog. |
> | **D) ❌ Incorrect** | dbt does not automatically retry post-hooks. |
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

- A) `{{ results }}` requires the `on-run-end` hook to be configured first before it's populated in post-hooks.
- B) `{{ results }}` is **only available in `on-run-end` hooks** — it returns `None` silently in `pre-hook` and `post-hook`.
- C) `{{ results }}` must be called as `{{ this.results }}` within a post-hook context.
- D) `{{ results }}` is populated only after the first model in a run completes — a single-model run always returns `None`.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `on-run-end` is independent — it doesn't "unlock" `results` for post-hooks. |
> | **B) ✅ Correct** | `{{ results }}` is **only available in `on-run-end` hooks** — it returns `None` in `pre-hook` and `post-hook` with no error or warning. This is a silent failure that can be hard to debug. The correct approach: use `{{ this }}` in post-hooks to reference the current model relation, and use `{{ results }}` only in `on-run-end` to access all run outcomes. |
> | **C) ❌ Incorrect** | `{{ this.results }}` is not valid syntax — `results` is a separate top-level variable, not an attribute of `this`. |
> | **D) ❌ Incorrect** | The number of models in a run has no bearing on `results` availability — the issue is the hook type, not run size. |
>
> > 💡 **Key rule**: `{{ results }}` = **`on-run-end` only**. In pre/post-hook = `None` (silent). Use `{{ this }}` in post-hooks.

---

### Q4.
> **Subdomain 9.4 — Multiple hooks accumulate**

A model has 2 post-hooks defined in `dbt_project.yml` and 3 post-hooks defined in the model's `config()` block. How many post-hooks execute when the model runs?

- A) 3 — model-level `config()` hooks override project-level hooks.
- B) 2 — project-level hooks take precedence over model-level hooks.
- C) 5 — all hooks from all scopes accumulate and execute in order.
- D) 2 — dbt deduplicates identical hooks automatically.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Model-level hooks do NOT override project-level hooks — they accumulate. |
> | **B) ❌ Incorrect** | Project-level hooks do NOT override model-level hooks either — all execute. |
> | **C) ✅ Correct** | Hooks from **all scopes accumulate** — they do not override each other. All 5 post-hooks execute: first the 2 project-level hooks (in definition order), then the 3 model-level `config()` block hooks (in definition order). Execution order: package → `dbt_project.yml` → `config()` block. Within each scope: top-to-bottom. |
> | **D) ❌ Incorrect** | dbt does not deduplicate hooks — even identical SQL statements would each execute once per scope level. |
>
> > 💡 **Key rule**: Hooks **accumulate** across scopes — they never override. All hooks from all scopes execute in scope order.

---

### Q5. ⭐
> **Subdomain 9.5 — VACUUM on Redshift: transaction: false**

A Redshift post-hook is designed to run `VACUUM SORT ONLY` after each model builds. The hook fails with a database error. What is the most likely cause and fix?

- A) Redshift doesn't support `VACUUM` commands in dbt hooks — use `dbt run-operation` instead.
- B) `VACUUM` on Redshift cannot run inside a transaction. Add `transaction: false` to the hook so it runs outside the model's transaction.
- C) `VACUUM SORT ONLY` syntax is deprecated in Redshift — use `VACUUM FULL` instead.
- D) Post-hooks can't run multi-word SQL commands — split the command into a macro.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `VACUUM` can be used in dbt hooks — the issue is transaction context, not hook type. Using `dbt run-operation` would work but isn't required. |
> | **B) ✅ Correct** | **Redshift's `VACUUM` command cannot run inside a transaction** — it's a DDL operation that must run outside any active transaction context. By default, post-hooks run inside the model's transaction. Fix: `post_hook: {sql: "VACUUM SORT ONLY {{this}}", transaction: false}`. The `transaction: false` flag runs the hook outside the transaction. |
> | **C) ❌ Incorrect** | `VACUUM SORT ONLY` is valid Redshift syntax — it's not deprecated. |
> | **D) ❌ Incorrect** | Multi-word SQL is valid in hook definitions. |
>
> > 💡 **Key rule**: Redshift `VACUUM` cannot run inside a transaction. Use `transaction: false` in the post-hook definition.

---

### Q6.
> **Subdomain 9.6 — on-run-end fires on partial failure**

A run includes 20 models. 3 models fail. An `on-run-end` hook is configured to send a Slack notification summarizing the run. Does the `on-run-end` hook fire?

- A) No — `on-run-end` only fires when the run completes successfully (all models pass).
- B) Yes — `on-run-end` fires after the run completes regardless of partial failures. The `results` variable contains entries for all resources including failures.
- C) Yes — but only if the `on-run-end` hook is defined with `transaction: false`.
- D) No — `on-run-end` is skipped when any model fails to prevent sending false success notifications.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `on-run-end` fires after the run regardless of success or failure — partial failure doesn't suppress it. |
> | **B) ✅ Correct** | `on-run-end` **always executes** after the run completes, even on partial failures. The `results` variable contains result objects for ALL resources that ran — including failed ones. Filter by `res.status == 'error'` to identify and report failures. This is what makes `on-run-end` powerful for alerting: it fires reliably and provides complete outcome data. |
> | **C) ❌ Incorrect** | `on-run-end` is not subject to model transaction context — it runs at the project level outside model transactions. `transaction: false` is relevant for `pre-hook`/`post-hook`, not `on-run-end`. |
> | **D) ❌ Incorrect** | Suppressing `on-run-end` on failure would defeat its main use case (alerting on failures). |
>
> > 💡 **Key rule**: `on-run-end` always fires — even on partial failure. Use `results` to detect and report failures.

---

### Q7.
> **Subdomain 9.7 — on-run-start and on-run-end configuration location**

A developer wants to add an `on-run-start` hook to resume a Snowflake warehouse before any models run. They add the hook to a model's `config()` block. The hook never fires. Why?

- A) `on-run-start` requires the `transaction: false` flag to fire correctly.
- B) `on-run-start` and `on-run-end` can only be configured in `dbt_project.yml` — they cannot be set in model `config()` blocks or YAML property files.
- C) The Snowflake warehouse resume command must use a specific macro format to work in hooks.
- D) `on-run-start` hooks only fire when running `dbt run` — not `dbt build` or other commands.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `transaction: false` is relevant for post-hooks that run SQL that can't be in a transaction — it has nothing to do with `on-run-start` configuration location. |
> | **B) ✅ Correct** | `on-run-start` and `on-run-end` are **project-level hooks** and can **only be configured in `dbt_project.yml`**. They cannot be defined in model `config()` blocks or YAML property files — those locations only support `pre-hook` and `post-hook`. This is a common mistake when developers confuse the scope of different hook types. |
> | **C) ❌ Incorrect** | The macro format is a separate concern — the root issue is where the hook is configured. |
> | **D) ❌ Incorrect** | `on-run-start` fires once per dbt command — this includes `dbt run`, `dbt build`, `dbt test`, `dbt seed`, `dbt snapshot`, `dbt compile`, and `dbt docs generate`. |
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

- A) Add `no_transaction: true` to the hook string.
- B) Use dictionary syntax: `{sql: "INSERT INTO audit_log ...", transaction: false}`.
- C) Use `on-run-end` instead of `post-hook` — it always runs outside transactions.
- D) Call the hook with `--no-transaction` flag in the dbt command.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `no_transaction: true` is not valid hook syntax. |
> | **B) ✅ Correct** | To run a hook **outside the model's transaction**, use the **dictionary syntax** with `transaction: false`: `post_hook: {sql: "INSERT INTO audit_log VALUES (...)", transaction: false}`. Without this, post-hooks run inside the model's transaction — if the model fails, the transaction rolls back and the hook never executes. Common use cases for `transaction: false`: audit logging (must persist on failure), VACUUM/ANALYZE on Redshift (cannot run inside a transaction), and cleanup operations that should always execute. |
> | **C) ❌ Incorrect** | `on-run-end` fires after the full run completes and is unrelated to individual model transaction behavior. Using it for per-model audit rows would require inspecting `results` to find which models ran, which is more complex. |
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

- A) config() block first → dbt_project.yml → package (model-level takes priority)
- B) Package → dbt_project.yml → config() block (outer scope first, inner scope last)
- C) All hooks run in random order — the order is not guaranteed
- D) dbt_project.yml → config() block → package (alphabetical by scope name)

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Model-level hooks do not take priority — they run last, not first. |
> | **B) ✅ Correct** | Hook execution order flows from **outermost to innermost scope**: (1) **Package-level hooks** run first; (2) **`dbt_project.yml` project-level hooks** run second; (3) **Model `config()` block / YAML property file hooks** run last. Within the same scope, hooks execute in **definition order** (top to bottom). All hooks from all scopes accumulate — model-level hooks never override project-level hooks. |
> | **C) ❌ Incorrect** | The order is deterministic and documented — it is not random. |
> | **D) ❌ Incorrect** | Alphabetical by scope name is not the ordering rule. |
>
> > 💡 **Key rule**: Hook order = **package → dbt_project.yml → config() block**. All hooks accumulate — none override others.

---

### Q11.
> **Subdomain 9.11 — {{ this }} context variable**

A post-hook needs to run a GRANT statement after a Snowflake model builds, granting SELECT to a reporter role on the exact table/view that was just created. Which context variable provides the fully-qualified relation object for the current model?

- A) `{{ model.name }}` — the model's identifier
- B) `{{ this }}` — the relation object for the current model (database.schema.identifier)
- C) `{{ target.schema }}.{{ model.name }}` — constructed from target and model name
- D) `{{ node.relation_name }}` — the canonical relation reference

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `{{ model.name }}` is just the model identifier string — it does not include database or schema, so it cannot be used in a GRANT statement that needs a fully-qualified reference. |
> | **B) ✅ Correct** | **`{{ this }}`** is the **relation object** for the current model — it resolves to the fully-qualified `database.schema.identifier` in the compiled hook SQL. It is available in both `pre-hook` and `post-hook`. The standard Snowflake GRANT pattern is: `GRANT SELECT ON {{ this }} TO ROLE reporter`. This is one of the most common hook use cases. |
> | **C) ❌ Incorrect** | While this could work in simple cases, it is fragile and not idiomatic. `{{ this }}` handles quoting and qualification correctly. |
> | **D) ❌ Incorrect** | `{{ node.relation_name }}` is not a documented standard context variable for hooks. |
>
> > 💡 **Key rule**: `{{ this }}` = fully-qualified relation object in pre/post-hooks. Standard for GRANT statements: `GRANT SELECT ON {{ this }} TO ROLE reporter`.

---

### Q12.
> **Subdomain 9.12 — on-run-end context variables**

An `on-run-end` hook needs to report two things: (1) which schemas were written to during the run, and (2) a list of results for every resource that ran. Which context variables provide these?

- A) `{{ target.schema }}` and `{{ results }}`
- B) `{{ schemas }}` (list of schemas) and `{{ results }}` (list of result objects for every resource)
- C) `{{ database_schemas }}` and `{{ run_results }}`
- D) `{{ this }}` and `{{ results }}`

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `{{ target.schema }}` is the primary target schema, not the full list of all schemas written to during the run. |
> | **B) ✅ Correct** | Two `on-run-end`-specific variables: **`{{ schemas }}`** — a list of all schemas written to during the run (useful for generating per-schema grants or reports). **`{{ results }}`** — a list of result objects for every resource that ran, each with `res.node.unique_id`, `res.status`, and `res.message`. Additionally, `{{ database_schemas }}` provides (database, schema) tuples for cross-database runs. These variables are ONLY available in `on-run-end` — they return `None` in pre-hook or post-hook. |
> | **C) ❌ Incorrect** | `{{ run_results }}` is not the documented variable name — it is `{{ results }}`. |
> | **D) ❌ Incorrect** | `{{ this }}` is a pre/post-hook variable representing the current model — it is not available in `on-run-end`. |
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

- A) `dbt run-operation` can only call macros that are in the `macros/` directory, not in `models/`.
- B) The macro must use `run_query()` or a `{% call statement() %}` block to execute SQL — simply returning a SQL string from a macro does not execute it.
- C) `DROP TABLE` requires a separate `--force` flag when called via `run-operation`.
- D) Macros called via `run-operation` run in read-only mode by default.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Macros for `run-operation` are in the `macros/` directory — this is correct. Location is not the issue. |
> | **B) ✅ Correct** | A macro called via `dbt run-operation` does **not** auto-execute SQL simply by returning a string. The macro must explicitly execute SQL using **`run_query()`** or a `{% call statement() %}` block. A macro that just templates SQL as a return value produces no warehouse side effect. Fix: `{% do run_query("DROP TABLE IF EXISTS " ~ target.schema ~ ".tmp_staging") %}`. |
> | **C) ❌ Incorrect** | There is no `--force` flag for `dbt run-operation`. |
> | **D) ❌ Incorrect** | `run-operation` macros run with full write access to the warehouse — there is no read-only default mode. |
>
> > 💡 **Key rule**: Operations don't auto-execute SQL return values. Must use `run_query()` or `{% call statement() %}` to actually execute SQL.

---

### Q14.
> **Subdomain 9.14 — dbt run-operation syntax**

A macro named `grant_schema_access` accepts two parameters: `role` and `schema_name`. How is this macro correctly invoked using `dbt run-operation`?

- A) `dbt run-operation grant_schema_access role=analyst schema_name=core`
- B) `dbt run-operation grant_schema_access --args '{role: analyst, schema_name: core}'`
- C) `dbt run-operation grant_schema_access --params '{"role": "analyst", "schema_name": "core"}'`
- D) `dbt run-operation --macro grant_schema_access --args role=analyst --args schema_name=core`

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Positional or keyword arguments passed directly after the macro name are not valid syntax for `dbt run-operation`. |
> | **B) ✅ Correct** | `dbt run-operation` passes arguments via the **`--args` flag** as a **YAML dictionary**: `dbt run-operation grant_schema_access --args '{role: analyst, schema_name: core}'`. Both YAML and JSON dict formats are accepted. The keys must exactly match the macro's parameter names. |
> | **C) ❌ Incorrect** | The flag is `--args`, not `--params`. |
> | **D) ❌ Incorrect** | The `--macro` flag does not exist. The macro name is a positional argument directly after `run-operation`. |
>
> > 💡 **Key rule**: `dbt run-operation <macro_name> --args '{key: value, key2: value2}'`. Args as YAML/JSON dict. Keys match macro parameter names exactly.

---

### Q15.
> **Subdomain 9.15 — Operations vs hooks**

A team needs to grant `SELECT` on all tables in the production schema to a `reporter` role. This grant must run once after each **full** deployment job (not per model). They are deciding between a `post-hook` and a `dbt run-operation`. Which approach is more appropriate and why?

- A) A `post-hook` on every model — this grants per table as each model builds.
- B) An `on-run-end` hook in `dbt_project.yml` — it fires once per dbt command, granting on all schemas after the job completes.
- C) A `dbt run-operation` step added to the job's command list — it is explicitly invoked once after the build completes, running an ad-hoc grant across all tables.
- D) Either approach works identically — the choice is stylistic.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Per-model post-hooks grant per table as each model builds — this works but means hundreds of individual GRANT statements rather than one bulk grant. |
> | **B) ✅ Correct** | An **`on-run-end` hook** configured in `dbt_project.yml` fires **once per dbt command** — after all models have built. It can run `GRANT SELECT ON ALL TABLES IN SCHEMA {{ target.schema }} TO ROLE reporter` in a single statement. This is more efficient than per-model grants and guarantees the grant runs after the full job, not piecemeal. `on-run-end` is specifically designed for this "run-level" automation pattern. (A `dbt run-operation` step in the job command list also works, but `on-run-end` is the idiomatic automated approach.) |
> | **C) ❌ Incorrect** | A `run-operation` step works, but `on-run-end` is the more idiomatic automated pattern for tasks tied to the job lifecycle. Operations are better for ad-hoc or one-time tasks. |
> | **D) ❌ Incorrect** | The approaches differ in automation (hooks are automatic) vs explicitness (operations are manual command steps). |
>
> > 💡 **Key rule**: Use `on-run-end` for automated run-level tasks (once per job). Use `run-operation` for ad-hoc or one-time commands.

---

### Q16.
> **Subdomain 9.16 — on-run-start/end fire frequency**

A team configures an `on-run-start` hook to log the run start time to an audit table. They run `dbt build` which executes 50 models. How many times does the `on-run-start` hook fire?

- A) 50 times — once per model
- B) 1 time — once per dbt command invocation
- C) 2 times — once at the start of `dbt run` and once at the start of `dbt test` (since `dbt build` internally executes both)
- D) 0 times — `on-run-start` only fires for `dbt run`, not `dbt build`

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `on-run-start` fires once per command invocation — not per model. Per-model execution is for `pre-hook`/`post-hook`. |
> | **B) ✅ Correct** | `on-run-start` fires **once per dbt command invocation** — regardless of how many models are in the run. For `dbt build` with 50 models, it fires exactly **once**. The same applies to `on-run-end`. These are project-level hooks, not resource-level. Also note: `on-run-start`/`on-run-end` fire for **every dbt command** that executes project resources — `dbt run`, `dbt build`, `dbt test`, `dbt seed`, `dbt snapshot`, `dbt compile`, `dbt docs generate`. |
> | **C) ❌ Incorrect** | `dbt build` is a single command invocation — it does not fire separate `on-run-start` hooks for its internal run and test phases. |
> | **D) ❌ Incorrect** | `on-run-start` fires for `dbt build`, `dbt run`, and all other resource-executing dbt commands. |
>
> > 💡 **Key rule**: `on-run-start`/`on-run-end` = once per dbt command, not per model. Fires for all resource-executing commands (run, build, test, seed, snapshot, compile).

---

### Q17.
> **Subdomain 9.17 — GRANT post-hooks on Snowflake**

A data platform team wants to automatically grant `SELECT` on every model to a `reporter` role after each model builds in Snowflake. They want this to apply to all models in the project. What is the recommended configuration?

- A) Add a `post-hook` to each model's `config()` block individually.
- B) Configure a `post-hook` in `dbt_project.yml` at the top level so it applies to all models globally, using `{{ this }}` to reference the current model's relation.
- C) Use `on-run-end` with `{{ schemas }}` to grant access to all schemas at once.
- D) Create a separate `dbt run-operation` step in every job's command list.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Per-model `config()` blocks require updating every model individually — not scalable for project-wide grants. |
> | **B) ✅ Correct** | The standard pattern for project-wide Snowflake grants is a **`post-hook` in `dbt_project.yml`** at the top level under `models:`: `post_hook: "GRANT SELECT ON {{ this }} TO ROLE reporter"`. This applies to every model in the project. `{{ this }}` resolves to the fully-qualified relation of each model. It's idiomatic, DRY, and requires no changes per model. This is one of the most common production hook patterns. |
> | **C) ❌ Incorrect** | `on-run-end` with `{{ schemas }}` grants on all tables in a schema at once — a valid bulk approach but less granular than per-model `{{ this }}` grants. The `post-hook` in `dbt_project.yml` is the more idiomatic per-model pattern. |
> | **D) ❌ Incorrect** | A `run-operation` per job requires manual setup in every job — not automatic and not recommended for routine operational grants. |
>
> > 💡 **Key rule**: Project-wide Snowflake GRANT = `post-hook` in `dbt_project.yml` with `GRANT SELECT ON {{ this }} TO ROLE reporter`.

---

### Q18.
> **Subdomain 9.18 — Calling macros from hooks**

A team has a macro `my_grant(relation, role)` that generates a GRANT statement. They want to call it from a `post-hook` on a model. What is the correct hook syntax?

- A) `post_hook: "my_grant(this, 'reporter')"`
- B) `post_hook: "{{ my_grant(this, 'reporter') }}"`
- C) `post_hook: "{{ my_grant({{ this }}, 'reporter') }}"`
- D) `post_hook: my_grant(this, 'reporter')`

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Without Jinja delimiters (`{{ }}`), the string is passed literally without macro evaluation. |
> | **B) ✅ Correct** | Hooks are strings evaluated as Jinja templates. To call a macro, wrap the entire call in Jinja: `"{{ my_grant(this, 'reporter') }}"`. The outer `{{ }}` tells dbt to evaluate the Jinja expression. Inside, `this` is the relation context variable (no extra curly braces needed). dbt evaluates the hook string as Jinja at runtime, calls `my_grant(this, 'reporter')`, and executes the returned SQL. |
> | **C) ❌ Incorrect** | `{{ {{ this }} }}` is invalid nested Jinja — it causes a compilation error. `this` inside a Jinja expression does not need extra `{{ }}`. |
> | **D) ❌ Incorrect** | Without Jinja delimiters, this is a literal string, not a macro call. |
>
> > 💡 **Key rule**: Macro call in hook = `"{{ macro_name(this, 'arg') }}"`. `this` inside `{{ }}` needs no additional delimiters.

---

### Q19.
> **Subdomain 9.19 — Hook accumulation**

A project uses a dbt package that defines a `post-hook` on all models. The `dbt_project.yml` also defines a `post-hook`. A model's `config()` block additionally defines a `post-hook`. A developer expects the model-level `config()` hook to override and replace the others. What actually happens?

- A) The model-level `config()` hook overrides all others — only the model's config() hook runs.
- B) The `dbt_project.yml` hook overrides the package hook, and the config() hook overrides both — only one hook runs.
- C) All three post-hooks run — hooks from all scopes **accumulate**, and no scope overrides another.
- D) The package hook is disabled when `dbt_project.yml` defines any hook, regardless of model config.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Model-level hooks do not override higher-scope hooks — they add to them. |
> | **B) ❌ Incorrect** | No hook scope overrides another. They all accumulate. |
> | **C) ✅ Correct** | Hooks in dbt **accumulate across all scopes** — they do not override each other. All three hooks run: the package hook, the `dbt_project.yml` hook, and the model's `config()` hook. They execute in order: package → project.yml → config() block. If you have 3 hooks at project level and 2 at model level, all 5 execute. This is an important distinction from how configs work in dbt (where more specific configs override less specific ones). Hooks are additive, not override-based. |
> | **D) ❌ Incorrect** | Package hooks are not disabled by project-level hook definitions. |
>
> > 💡 **Key rule**: Hooks **accumulate** — they never override. All hooks from all scopes run. Configs override; hooks add.

---

### Q20.
> **Subdomain 9.20 — on-run-end results object**

An `on-run-end` hook sends a summary notification. A developer needs to count how many models succeeded and how many errored. They use `{{ results }}` in the hook. What is the structure of each object in `results`, and how do they filter for errors?

- A) Each result is a string like `"model_name: success"` — filter with `if 'error' in res`.
- B) Each result object has `res.node.unique_id`, `res.status` (values: `success`, `error`, `skipped`), and `res.message`. Filter errors with `{% if res.status == 'error' %}`.
- C) `results` is a dictionary keyed by model name — access error status with `results['model_name']['status']`.
- D) Each result has `res.model` (name) and `res.passed` (boolean) — filter with `{% if not res.passed %}`.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Results are not string values. They are structured objects with named properties. |
> | **B) ✅ Correct** | Each object in `{{ results }}` has: **`res.node.unique_id`** (e.g., `model.project.model_name`), **`res.status`** (one of `success`, `error`, `skipped`, `warn`, `pass`, `fail`), and **`res.message`** (error or completion message). To count errors: `{% set error_count = results | selectattr("status", "equalto", "error") | list | length %}`. The results list includes all resources that ran, even partial failures — making it ideal for run-level reporting in `on-run-end`. |
> | **C) ❌ Incorrect** | `results` is a list, not a dictionary. Access is by iteration, not by key. |
> | **D) ❌ Incorrect** | `res.passed` is not a documented property. The status field uses string values, not a boolean. |
>
> > 💡 **Key rule**: `results` list — each item has `res.node.unique_id`, `res.status` (`success`/`error`/`skipped`), `res.message`. Filter: `selectattr("status", "equalto", "error")`.

---

*[End of Topic 9 — 20 questions]*

