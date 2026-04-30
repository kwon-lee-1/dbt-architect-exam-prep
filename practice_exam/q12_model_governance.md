# Topic 10: Model Governance (Access, Contracts, Versions, Groups) — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 5 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 10.1 — `access: public` does not grant database permissions**

In an Enterprise dbt Mesh, a consumer project's production job references a producer's `dim_customers` model via `{{ ref('jaffle_finance', 'dim_customers') }}`. The model is marked `access: public`, `dependencies.yml` is correct, and the job parses and compiles without error. At runtime, Snowflake returns `SQL access control error: Insufficient privileges to operate on table 'DIM_CUSTOMERS'`. What is the root cause?

- A) `access: public` requires the producer to add the consumer project to an `allowed_consumers` list in the model's YAML — without it, the warehouse layer blocks access.
- B) The producer project is missing a Staging environment, so the consumer's Production job fell back to Production credentials that lack cross-project grants.
- C) `access: public` is a DAG-level governance control only — it does not grant warehouse SELECT privileges; grants must be configured separately via `grants`, post-hooks, or role-based access in the warehouse.
- D) Cross-project refs to public models require the consumer's service account to be added to the producer project's "Cross-project Readers" group in dbt Cloud.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | No `allowed_consumers` config exists in dbt. `access: public` is unconditionally visible across projects — there is no per-consumer allowlist at the model level. |
> | **B) ❌ Incorrect** | Staging environment fallback affects cross-project **ref resolution**, not warehouse permissions. The scenario states the job compiled successfully — resolution worked. The failure is at query execution, which is a warehouse grants issue. |
> | **C) ✅ Correct** | `access` levels (`private`/`protected`/`public`) are purely **DAG-level governance** — they control whether `ref()` is permitted across groups/projects at parse/compile time. They do **not** touch warehouse permissions. The consumer's warehouse role still needs `USAGE` on the schema and `SELECT` on the table, configured via `grants:` in the producer's YAML, a post-hook, or direct role management. |
> | **D) ❌ Incorrect** | No such "Cross-project Readers" group exists in dbt Cloud. The concept conflates RBAC permissions with governance access, which are orthogonal. |
>
> > 💡 **Key rule**: `access: public` = who can `ref()` you in code. Warehouse `GRANT SELECT` = who can query the underlying table. These are two independent layers — always configure both for cross-project Mesh consumers.

---

### Q2. ⭐
> **Subdomain 10.2 — Package `restrict-access` default**

A platform team publishes a dbt package containing both `protected` and `private` models intended for internal use only, plus a few `public` models. A downstream team installs the package via `packages.yml` and discovers they can successfully `ref()` the **protected** models from the installed package. The platform team expected only the `public` models to be accessible. What is the cause, and what is the fix?

- A) This is expected behavior — `protected` access allows refs from any installed package by design. To prevent it, change the protected models to `private`.
- B) By default, installed packages expose all non-private models to the consuming project. The platform team must set `restrict-access: True` in the package's `dbt_project.yml` to force consumers to only reference `public` models.
- C) The package manifest is stale — running `dbt deps --upgrade` in the consumer project will re-validate access levels and block the protected refs.
- D) Packages do not participate in the governance access system. Protected/private only work within dbt Mesh `project_dependencies`, not via `packages.yml`.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `protected` (the default) means "same project or installed package" — it deliberately permits refs from installed packages. Changing everything to `private` would break internal refs within the package itself across groups. |
> | **B) ✅ Correct** | The default `protected` behavior intentionally treats an installed package as an extension of the consumer project. To enforce strict public-only sharing, the producing package must set **`restrict-access: True`** in its `dbt_project.yml`. This changes the effective boundary so consumers can only ref models explicitly marked `public`. |
> | **C) ❌ Incorrect** | `dbt deps --upgrade` refreshes package versions; it does not change access enforcement semantics. |
> | **D) ❌ Incorrect** | Packages do participate in the access system — `protected` specifically permits refs from installed packages. The interaction is documented, not absent. |
>
> > 💡 **Key rule**: `protected` + installed package = consumer can ref. To block that, producer sets `restrict-access: True` in its `dbt_project.yml`. This is distinct from Mesh `project_dependencies`, which already enforces public-only by default.

---

### Q3. ⭐
> **Subdomain 10.3 — Migration path for breaking change on contracted public model**

A public, contract-enforced model `dim_customers` (current `latest_version: 1`) must drop the `country_name` column. Three downstream Mesh consumer projects pin `v=1` in their refs. The architect needs a zero-downtime migration path. Which sequence is correct?

- A) Update `dim_customers.sql` to drop the column, update the YAML `columns:` list to remove `country_name`, and deploy. The contract will allow it because SQL and YAML remain consistent.
- B) Set `on_schema_change: sync_all_columns` on the model and deploy. The contract handles column removal automatically when this config is present.
- C) Add a `v=2` with the column removed, bump `latest_version: 2`, set a `deprecation_date` on `v=1`, notify consumers to migrate their pinned refs, then remove `v=1` after the deprecation date. Never modify `v=1` in place.
- D) Mark the model `access: protected` temporarily, drop the column, then flip back to `access: public` after all consumers redeploy.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Contracts do not just check SQL/YAML consistency — they treat column removal as a **breaking change** regardless of whether both sides are updated. The preflight check compares the new contract to the previous one and fails the build. For a **versioned** contracted model, removing it outright raises a hard error (vs a warning for unversioned). |
> | **B) ❌ Incorrect** | `on_schema_change: sync_all_columns` is **not compatible** with contracts at all. Incremental + contract supports only `append_new_columns` or `fail`. This option would itself raise a configuration error. |
> | **C) ✅ Correct** | This is the documented migration pattern: create `dim_customers_v2.sql` without the column, set `latest_version: 2`, add `deprecation_date` on `v=1` which triggers warnings for pinned consumers, let consumers migrate at their own pace, and only remove `v=1` once the deprecation date passes. This preserves downstream stability through the migration window. |
> | **D) ❌ Incorrect** | Flipping `access` does not suspend contract enforcement. The contract breaking change is detected at build time regardless of access level. Toggling access also doesn't give consumers any migration window — their pinned refs would still break. |
>
> > 💡 **Key rule**: Breaking change on a contracted public model = **new version + `deprecation_date` + consumer migration + delete old version**. Never modify a contracted public model in place — the contract is designed to block exactly that.

---

### Q4. ⭐
> **Subdomain 10.4 — `latest_version` implicit resolution and prerelease semantics**

An architect declares two versions of `dim_customers` in YAML: `v=1` and `v=2`. They omit the `latest_version:` key. A separate model contains an unpinned `{{ ref('dim_customers') }}`. Later, the architect adds `latest_version: 1` explicitly to the YAML (while `v=2` still exists). What is the behavior in each state, and what is `v=2` considered in the second state?

- A) State 1: unpinned ref resolves to `v=1` (alphabetical first). State 2: unpinned ref resolves to `v=1`. `v=2` is treated as deprecated.
- B) State 1: parse error — `latest_version` is required when multiple versions exist. State 2: unpinned ref resolves to `v=1`; `v=2` is considered a **prerelease**.
- C) State 1: unpinned ref resolves to `v=2` (highest version number by default). State 2: unpinned ref resolves to `v=1`; `v=2` is considered a **prerelease** and dbt emits a warning that unpinned refs will eventually resolve to it.
- D) State 1: unpinned refs fail to compile without an explicit `latest_version`. State 2: `v=2` is silently ignored until `latest_version` is bumped.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Version resolution is **numeric**, not alphabetical. And `v=2` is not "deprecated" — deprecation requires an explicit `deprecation_date`. |
> | **B) ❌ Incorrect** | `latest_version` is **not required**; dbt implicitly picks the highest numeric version. So State 1 parses fine and resolves to `v=2`. |
> | **C) ✅ Correct** | **State 1** (no `latest_version` declared): dbt uses the numerically highest version → unpinned `ref()` resolves to `v=2`. **State 2** (`latest_version: 1` explicit, `v=2` exists): unpinned `ref()` resolves to `v=1`, and `v=2` is classified as a **prerelease**. dbt emits a warning like: "A prerelease version 2 is available…this reference will resolve to v=2 when latest_version is bumped." This lets teams ship a new version in code and let consumers adopt it before cutting over. |
> | **D) ❌ Incorrect** | Omitting `latest_version` does not cause compilation failure. `v=2` is never silently ignored — it becomes a prerelease, visible and refable by explicit pin. |
>
> > 💡 **Key rule**: No `latest_version` → highest number wins. Explicit `latest_version` lower than the highest → newer versions are **prereleases** (shipped but not yet the default). Use this to stage a new version before flipping consumers over.

---

### Q5. ⭐
> **Subdomain 10.5 — Model group gotchas**

Which of the following statements about model **governance groups** (not RBAC user groups) are correct? **Select TWO correct answers.**

- A) The `owner:` property on a group requires **both** `name` and `email` — omitting either causes a parse error.
- B) A model can belong to **exactly one** group; attempting to assign multiple groups via both `dbt_project.yml` and an in-file `{{ config() }}` causes the most specific declaration (in-file) to win, not a merge.
- C) Referencing a `private` model from outside its group causes a `DbtReferenceError` at **parse time**, not at runtime — the model never builds.
- D) Group assignments defined in `dbt_project.yml` (via `+group:`) cannot be overridden by schema.yml or inline `config()` — they are locked at the project level.
- E) The list of users in a dbt Cloud RBAC group named `finance` is automatically synced to the governance group `finance`, granting those users the ability to ref private models in the `finance` governance group.

> [!success]- Answer & Explanations
> **✅ Correct: B, C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The `owner:` property requires `name` **OR** `email` — either one is sufficient. Both are not mandatory. |
> | **B) ✅ Correct** | A model belongs to exactly one group. The three assignment methods (`+group:` in `dbt_project.yml`, `group:` in schema.yml, `{{ config(group='...') }}` in-file) follow dbt's standard config precedence: **in-file > schema.yml > project-level**. The most specific declaration wins — there is no merging of groups. |
> | **C) ✅ Correct** | Private access violations are caught at **parse time** (during `dbt compile` or the manifest build), not at runtime. dbt raises a `DbtReferenceError`: "the referenced node is private to the [group name]." The offending model never gets to the database. This early detection is the core value of governance groups. |
> | **D) ❌ Incorrect** | This is the opposite of dbt's config precedence. Project-level `+group:` provides a default that can be overridden by more specific declarations in schema.yml or in-file config — the same pattern as all other dbt config. |
> | **E) ❌ Incorrect** | Governance groups (defined in dbt YAML, control which models can ref private models) and RBAC user groups (defined in dbt Cloud, control which humans can access the UI/IDE/jobs) are **completely orthogonal**. Matching names is pure coincidence and creates no linkage — governance membership is a property of models, not users. |
>
> > 💡 **Key rule**: Governance groups are code-level model ownership boundaries with standard dbt config precedence (in-file > schema.yml > project). Violations caught at parse time. Never conflate them with RBAC user groups — they share nothing but naming conventions.

---

*[End of Topic 10 — 5 questions]*
